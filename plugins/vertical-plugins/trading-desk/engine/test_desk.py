#!/usr/bin/env python3
"""Tests for the desk risk engine. Run: python3 -m unittest test_desk -v"""
import contextlib
import io
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

import desk
from desk import D


def fresh(capital="200", **config):
    """An in-memory ledger, bypassing the CLI."""
    state = {
        "currency": "GBP", "opened": "2026-01-01",
        "starting_capital": capital, "cash": capital, "high_water_mark": capital,
        "realised_pnl": "0", "halted": False, "halt_reason": None,
        "positions": {}, "trades": [], "config": dict(desk.DEFAULT_CONFIG),
    }
    state["config"].update({k: str(v) for k, v in config.items()})
    return state


def pos(qty, avg, mark, stop, venue="uk", fees="0"):
    return {"qty": str(qty), "avg_price": str(avg), "mark": str(mark), "stop": str(stop),
            "venue": venue, "fees_paid": str(fees), "opened": "2026-01-01", "thesis": ""}


class TestFloor(unittest.TestCase):
    def test_phase1_floor_is_drawdown_on_starting_capital(self):
        s = fresh()
        self.assertFalse(desk.armed(s))
        self.assertEqual(desk.floor(s), D("140"))  # 200 * (1 - 0.30)

    def test_floor_arms_at_threshold_and_protects_75pc_of_earnings(self):
        s = fresh()
        s["high_water_mark"] = "1000"
        self.assertTrue(desk.armed(s))
        # 200 + 0.75 * (1000 - 200) = 800
        self.assertEqual(desk.floor(s), D("800"))

    def test_floor_ratchets_with_the_high_water_mark(self):
        s = fresh()
        s["high_water_mark"] = "2000"
        # 200 + 0.75 * 1800 = 1550
        self.assertEqual(desk.floor(s), D("1550"))

    def test_floor_never_falls_when_equity_falls(self):
        s = fresh()
        s["high_water_mark"] = "1600"
        s["cash"] = "900"
        high_floor = desk.floor(s)
        s["cash"] = "820"          # equity drops
        self.assertEqual(desk.floor(s), high_floor)

    def test_floor_stays_armed_once_touched(self):
        """Equity falling back under the threshold must not disarm protection."""
        s = fresh()
        s["high_water_mark"] = "1000"
        s["cash"] = "850"          # equity now below the 1000 threshold
        self.assertTrue(desk.armed(s))
        self.assertEqual(desk.floor(s), D("800"))

    def test_hwm_only_moves_up(self):
        s = fresh()
        s["cash"] = "300"
        desk.update_hwm(s)
        self.assertEqual(D(s["high_water_mark"]), D("300"))
        s["cash"] = "250"
        desk.update_hwm(s)
        self.assertEqual(D(s["high_water_mark"]), D("300"))


class TestRisk(unittest.TestCase):
    def test_position_risk_is_distance_to_stop(self):
        self.assertEqual(desk.position_risk(pos(100, 2, 3, 2.5)), D("50"))

    def test_position_stopping_in_profit_carries_no_downside(self):
        """Stop above the mark means the position cannot lose money from here."""
        self.assertEqual(desk.position_risk(pos(100, 2, 3, 3.2)), D("0"))

    def test_equity_at_risk_nets_off_all_stops(self):
        s = fresh()
        s["cash"] = "100"
        s["positions"] = {"A": pos(100, 1, 1, "0.9"), "B": pos(50, 2, 2, "1.8")}
        self.assertEqual(desk.equity(s), D("300"))      # 100 cash + 100 + 100
        self.assertEqual(desk.open_risk(s), D("20"))    # 10 + 10
        self.assertEqual(desk.equity_at_risk(s), D("280"))


class TestCosts(unittest.TestCase):
    def test_uk_buy_pays_stamp_duty_and_uk_sale_does_not(self):
        s = fresh()
        self.assertEqual(desk.buy_cost(s, D("200"), "uk"), D("1.00"))   # 0.5%
        self.assertEqual(desk.sell_cost(s, D("200"), "uk"), D("0.00"))

    def test_us_pays_fx_both_ways_and_no_stamp_duty(self):
        s = fresh()
        self.assertEqual(desk.buy_cost(s, D("200"), "us"), D("0.30"))   # 0.15%
        self.assertEqual(desk.sell_cost(s, D("200"), "us"), D("0.30"))

    def test_commission_applies_per_side(self):
        s = fresh(commission="11.95")
        self.assertEqual(desk.buy_cost(s, D("200"), "uk"), D("12.95"))
        self.assertEqual(desk.sell_cost(s, D("200"), "uk"), D("11.95"))

    def test_breakeven_sits_above_entry_by_the_cost_load(self):
        s = fresh()
        p = pos(50, 4, 4, 3.6, venue="uk", fees="1.00")
        be = desk.breakeven(s, p)
        self.assertGreater(be, D("4"))
        self.assertAlmostEqual(float(be), 4.02, places=2)   # 200 + 1.00 fees over 50 shares


class TestCLI(unittest.TestCase):
    """End-to-end through the CLI against a temp ledger."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.f = str(Path(self.dir.name) / "l.json")
        self.run_ok("init", "--capital", "200")

    def tearDown(self):
        self.dir.cleanup()

    def state(self):
        return json.loads(Path(self.f).read_text())

    def run_ok(self, *args):
        """Drive the CLI, swallowing its report output."""
        with contextlib.redirect_stdout(io.StringIO()):
            desk.main(["--file", self.f, *args])

    def test_buy_debits_cash_including_fees(self):
        self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                    "--stop", "3.7", "--venue", "uk")
        s = self.state()
        # 160 notional + 0.80 stamp duty
        self.assertEqual(D(s["cash"]), D("39.20"))
        self.assertEqual(D(s["positions"]["AAA"]["qty"]), D("40"))

    def test_buy_over_per_trade_risk_limit_is_rejected(self):
        # Stop 50% away on a 160 notional risks 80, way over 8% of 200 = 16.
        with self.assertRaises(SystemExit):
            self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                        "--stop", "2", "--venue", "uk")
        self.assertEqual(self.state()["positions"], {})

    def test_buy_beyond_available_cash_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_ok("buy", "--ticker", "AAA", "--qty", "1000", "--price", "4",
                        "--stop", "3.9", "--venue", "uk")

    def test_sub_minimum_notional_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_ok("buy", "--ticker", "AAA", "--qty", "5", "--price", "4",
                        "--stop", "3.8", "--venue", "uk")

    def test_force_records_the_breach_rather_than_hiding_it(self):
        """A ledger must be able to record what actually happened."""
        self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                    "--stop", "2", "--venue", "uk", "--force")
        t = self.state()["trades"][-1]
        self.assertTrue(t["forced"])
        self.assertTrue(t["breaches"])

    def test_stop_must_be_below_entry(self):
        with self.assertRaises(SystemExit):
            self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                        "--stop", "4.5", "--venue", "uk")

    def test_max_positions_is_enforced(self):
        for t in ("AAA", "BBB", "CCC"):
            self.run_ok("buy", "--ticker", t, "--qty", "15", "--price", "4",
                        "--stop", "3.8", "--venue", "uk")
        with self.assertRaises(SystemExit):
            self.run_ok("buy", "--ticker", "DDD", "--qty", "10", "--price", "4",
                        "--stop", "3.8", "--venue", "uk")

    def test_sell_realises_pnl_net_of_both_sides_costs(self):
        self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                    "--stop", "3.7", "--venue", "uk")
        self.run_ok("sell", "--ticker", "AAA", "--price", "4.5")
        s = self.state()
        # gross 20.00, less 0.80 stamp duty on entry, no sell-side UK fee
        self.assertEqual(D(s["realised_pnl"]), D("19.20"))
        self.assertNotIn("AAA", s["positions"])
        self.assertEqual(D(s["cash"]), D("219.20"))

    def test_partial_sell_keeps_the_remainder(self):
        self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                    "--stop", "3.7", "--venue", "uk")
        self.run_ok("sell", "--ticker", "AAA", "--qty", "20", "--price", "4.5")
        s = self.state()
        self.assertEqual(D(s["positions"]["AAA"]["qty"]), D("20"))

    def test_averaging_up_reprices_the_book(self):
        self.run_ok("buy", "--ticker", "AAA", "--qty", "20", "--price", "4",
                    "--stop", "3.8", "--venue", "uk")
        self.run_ok("buy", "--ticker", "AAA", "--qty", "20", "--price", "5",
                    "--stop", "4.8", "--venue", "uk")
        p = self.state()["positions"]["AAA"]
        self.assertEqual(D(p["qty"]), D("40"))
        self.assertEqual(D(p["avg_price"]), D("4.5"))

    def test_widening_a_stop_is_refused(self):
        self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                    "--stop", "3.7", "--venue", "uk")
        with self.assertRaises(SystemExit):
            self.run_ok("stop", "--ticker", "AAA", "--price", "3.0")
        self.assertEqual(D(self.state()["positions"]["AAA"]["stop"]), D("3.7"))

    def test_tightening_a_stop_is_allowed(self):
        self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                    "--stop", "3.7", "--venue", "uk")
        self.run_ok("stop", "--ticker", "AAA", "--price", "3.9")
        self.assertEqual(D(self.state()["positions"]["AAA"]["stop"]), D("3.9"))

    def test_breaching_the_floor_halts_the_desk(self):
        self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                    "--stop", "3.7", "--venue", "uk")
        self.run_ok("mark", "--ticker", "AAA", "--price", "2.0")   # equity ~119 < floor 140
        s = self.state()
        self.assertTrue(s["halted"])
        self.assertIn("protected floor", s["halt_reason"])

    def test_halted_desk_refuses_new_buys(self):
        self.run_ok("buy", "--ticker", "AAA", "--qty", "40", "--price", "4",
                    "--stop", "3.7", "--venue", "uk")
        self.run_ok("mark", "--ticker", "AAA", "--price", "2.0")
        with self.assertRaises(SystemExit):
            self.run_ok("buy", "--ticker", "BBB", "--qty", "10", "--price", "4",
                        "--stop", "3.8", "--venue", "uk")

    def test_crossing_the_threshold_makes_a_wide_stop_non_compliant(self):
        """The point of the rule: at £1,000 you must derisk immediately."""
        self.run_ok("buy", "--ticker", "AAA", "--qty", "49", "--price", "4",
                    "--stop", "3.7", "--venue", "uk")
        self.run_ok("mark", "--ticker", "AAA", "--price", "20.55")
        s = self.state()
        self.assertTrue(desk.armed(s))
        self.assertLess(desk.equity_at_risk(s), desk.floor(s))
        # Tightening the stop restores compliance without selling.
        self.run_ok("stop", "--ticker", "AAA", "--price", "17.00")
        s = self.state()
        self.assertGreaterEqual(desk.equity_at_risk(s), desk.floor(s))


if __name__ == "__main__":
    unittest.main(verbosity=2)
