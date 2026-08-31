/* ==========================================================================
   Debrett's Portfolio Reporting — application

   Six views over one data set:
     portfolio    the board's opening screen
     company      a single company's tear sheet
     benchmarks   one company against the portfolio cohort
     collection   what has been asked for and what has landed
     submit       the portfolio company's own quarterly return
     board pack   the printable A4 landscape extract
   ========================================================================== */

/* ----------------------------------------------------------------- state -- */

const state = {
  view: 'portfolio',
  windowN: 8,
  sector: 'all',
  companyId: DATA.companies[0].id,
};

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const slot = (name) => $(`[data-slot="${name}"]`);

/* ----------------------------------------------------------- derivations -- */

const sum = (a) => a.reduce((t, v) => t + v, 0);
const last = (a) => a[a.length - 1];

/** Trailing twelve months — the last four quarters of a quarterly series. */
const ltm = (values) => sum(values.slice(-4));
/** The four quarters before those, for a like-for-like comparison. */
const priorLtm = (values) => sum(values.slice(-8, -4));

function ltmGrowth(values) {
  const prior = priorLtm(values);
  if (!prior) return null;
  return (ltm(values) / prior - 1) * 100;
}

const marginPct = (num, den) => (den ? (num / den) * 100 : null);

/** Monthly net cash burn, taken from the last quarter's movement. */
function monthlyBurn(cash) {
  const move = cash[cash.length - 2] - last(cash);
  return move / 3;
}

function runwayMonths(cash) {
  const burn = monthlyBurn(cash);
  if (burn <= 0) return Infinity;
  return last(cash) / burn;
}

/** Runway drives an escalation, so it wears status tokens, never series ink. */
function runwayTone(months) {
  if (!Number.isFinite(months)) return 'good';
  if (months < 6) return 'critical';
  if (months < 12) return 'serious';
  if (months < 18) return 'warning';
  return 'good';
}

const REPORTING_TONE = { received: 'good', late: 'serious', outstanding: 'critical' };
const REPORTING_LABEL = { received: 'Received', late: 'Received late', outstanding: 'Outstanding' };

function activeCompanies() {
  return DATA.companies.filter((c) => state.sector === 'all' || c.sector === state.sector);
}

function currentCompany() {
  return DATA.companies.find((c) => c.id === state.companyId) || activeCompanies()[0];
}

const periods = () => DATA.periods.slice(-state.windowN);
const win = (values) => values.slice(-state.windowN);

/** Sum a metric across the companies currently in scope, period by period. */
function aggregate(key) {
  const cs = activeCompanies();
  return DATA.periods.map((_, i) => sum(cs.map((c) => c.series[key][i])));
}

const seriesColour = (n) => [
  getComputedStyle(document.documentElement).getPropertyValue('--s1').trim(),
  getComputedStyle(document.documentElement).getPropertyValue('--s2').trim(),
  getComputedStyle(document.documentElement).getPropertyValue('--s3').trim(),
][n];

/* -------------------------------------------------------- shared pieces -- */

function statTile({ label, value, delta, deltaTone, sparkValues, hero = false, bare = false, note }) {
  const kids = [
    h('div', { class: 'stat__label', text: label }),
    h('div', { class: 'stat__value', text: value }),
  ];
  if (delta) {
    kids.push(h('div', { class: `stat__delta${deltaTone ? ` delta--${deltaTone}` : ''}` }, [
      deltaTone ? h('span', { class: 'delta__mark', 'aria-hidden': 'true', text: deltaTone === 'good' ? '▲' : deltaTone === 'bad' ? '▼' : '—' }) : null,
      h('span', { text: delta }),
    ]));
  }
  if (note) kids.push(h('div', { class: 'stat__delta', text: note }));
  if (sparkValues) {
    kids.push(h('div', { class: 'stat__spark' }, [
      sparkline(sparkValues, { ariaLabel: `${label}, ${sparkValues.length} quarters to ${last(periods())}` }),
    ]));
  }
  return h('div', { class: `stat${hero ? ' stat--hero' : ''}${bare ? ' stat--bare' : ''}` }, kids);
}

function panel(title, subtitle, children) {
  return h('section', { class: 'panel' }, [
    h('div', { class: 'panel__head' }, [
      h('h3', { class: 'panel__title', text: title }),
      subtitle ? h('p', { class: 'panel__sub', text: subtitle }) : null,
    ]),
    ...[].concat(children),
  ]);
}

function section(title, note, children) {
  return h('section', { class: 'section' }, [
    h('div', { class: 'section__head' }, [
      h('h3', { class: 'section__title', text: title }),
      note ? h('p', { class: 'section__note', text: note }) : null,
    ]),
    ...[].concat(children),
  ]);
}

/* ============================================================= portfolio == */

function renderPortfolio() {
  const host = slot('portfolio');
  host.textContent = '';
  const cs = activeCompanies();
  const ps = periods();

  const rev = aggregate('revenue');
  const gp = aggregate('grossProfit');
  const ebitda = aggregate('ebitda');

  const revLtm = ltm(rev);
  const revGrowth = ltmGrowth(rev);
  const ebitdaLtm = ltm(ebitda);
  const invested = sum(cs.map((c) => c.invested));
  const carrying = sum(cs.map((c) => c.carryingValue));

  const onTime = cs.filter((c) => c.reporting.status === 'received').length;
  const shortRunway = cs.filter((c) => runwayMonths(c.series.cash) < 12);

  /* Exactly one hero figure per view. */
  host.append(section(
    `Portfolio at ${DATA.meta.currentPeriod}`,
    `${cs.length} companies in scope · figures are trailing twelve months to ${DATA.meta.currentPeriod}`,
    h('div', { class: 'grid grid--stats' }, [
      statTile({
        hero: true,
        label: 'Portfolio revenue (LTM)',
        value: Fmt.millions(revLtm),
        delta: `${Fmt.signedPct(revGrowth)} year on year`,
        deltaTone: revGrowth >= 0 ? 'good' : 'bad',
        sparkValues: win(rev),
      }),
      statTile({
        label: 'Portfolio EBITDA (LTM)',
        value: Fmt.millions(ebitdaLtm),
        delta: `${Fmt.signedPct(marginPct(ebitdaLtm, revLtm), 1)} margin`,
        sparkValues: win(ebitda),
      }),
      statTile({
        label: 'Invested / carrying value',
        value: `${Fmt.millions(invested)} / ${Fmt.millions(carrying)}`,
        note: `${(carrying / invested).toFixed(2)}× gross multiple on invested capital`,
      }),
      statTile({
        label: `Returns in for ${DATA.meta.currentPeriod}`,
        value: `${onTime} of ${cs.length}`,
        note: `Due ${Fmt.date(DATA.meta.dueDate)}`,
      }),
      statTile({
        label: 'Under twelve months of runway',
        value: String(shortRunway.length),
        note: shortRunway.length ? shortRunway.map((c) => c.name).join(', ') : 'No company below the threshold',
      }),
    ]),
  ));

  host.append(section('Trading', null, h('div', { class: 'grid grid--2' }, [
    panel(
      'Revenue, gross profit and EBITDA',
      'Portfolio aggregate, £m by quarter',
      lineChart({
        categories: ps,
        series: [
          { name: 'Revenue', values: win(rev), color: seriesColour(0) },
          { name: 'Gross profit', values: win(gp), color: seriesColour(1) },
          { name: 'EBITDA', values: win(ebitda), color: seriesColour(2) },
        ],
        format: (v) => Fmt.millions(v, 2),
        yFormat: (v) => (v / 1000).toFixed(1),
        tableCaption: 'Portfolio aggregate by quarter, £m',
        ariaLabel: 'Portfolio revenue, gross profit and EBITDA by quarter',
      }),
    ),
    panel(
      'Revenue by quarter',
      'Portfolio aggregate, £m',
      columnChart({
        categories: ps,
        values: win(rev),
        color: seriesColour(0),
        seriesName: 'Revenue',
        format: (v) => Fmt.millions(v, 2),
        yFormat: (v) => (v / 1000).toFixed(1),
        tableCaption: 'Portfolio revenue by quarter, £m',
        ariaLabel: 'Portfolio revenue by quarter',
      }),
    ),
  ])));

  /* Company table — the detail behind the tiles. */
  const table = h('table', { class: 'data' });
  table.append(h('caption', { text: `Trailing twelve months to ${DATA.meta.currentPeriod}. Click a company for its tear sheet.` }));
  table.append(h('thead', {}, [h('tr', {}, [
    h('th', { scope: 'col', text: 'Company' }),
    h('th', { scope: 'col', text: 'Trend' }),
    h('th', { scope: 'col', class: 'n', text: 'Revenue LTM' }),
    h('th', { scope: 'col', class: 'n', text: 'YoY' }),
    h('th', { scope: 'col', class: 'n', text: 'Gross margin' }),
    h('th', { scope: 'col', class: 'n', text: 'EBITDA margin' }),
    h('th', { scope: 'col', class: 'n', text: 'Runway' }),
    h('th', { scope: 'col', text: `${DATA.meta.currentPeriod} return` }),
  ])]));
  const body = h('tbody');
  for (const c of cs) {
    const r = ltm(c.series.revenue);
    const g = ltmGrowth(c.series.revenue);
    const months = runwayMonths(c.series.cash);
    const nameBtn = h('button', { class: 'linkcell', type: 'button', text: c.name });
    nameBtn.addEventListener('click', () => { state.companyId = c.id; go('company'); });
    body.append(h('tr', {}, [
      h('td', {}, [nameBtn, h('span', { class: 'cell-sub', text: `${c.sector} · ${c.stage}` })]),
      h('td', {}, [sparkline(win(c.series.revenue), { ariaLabel: `${c.name} revenue trend` })]),
      h('td', { class: 'n', text: Fmt.millions(r) }),
      h('td', { class: 'n', text: Fmt.signedPct(g) }),
      h('td', { class: 'n', text: Fmt.pct(marginPct(ltm(c.series.grossProfit), r)) }),
      h('td', { class: 'n', text: Fmt.pct(marginPct(ltm(c.series.ebitda), r)) }),
      h('td', { class: 'n' }, [statusMark(runwayTone(months), Fmt.months(months))]),
      h('td', {}, [statusMark(REPORTING_TONE[c.reporting.status], REPORTING_LABEL[c.reporting.status])]),
    ]));
  }
  table.append(body);
  host.append(section('Companies', 'Runway is cash at quarter end divided by the latest quarter’s monthly net burn.',
    h('div', { class: 'tablewrap' }, [table])));
}

/* =============================================================== company == */

function renderCompany() {
  const host = slot('company');
  host.textContent = '';
  const c = currentCompany();
  if (!c) { host.append(h('p', { text: 'No company in scope for this filter.' })); return; }
  const ps = periods();

  const r = ltm(c.series.revenue);
  const months = runwayMonths(c.series.cash);
  const growth = ltmGrowth(c.series.revenue);

  host.append(h('div', { class: 'tearhead' }, [
    h('div', {}, [
      h('div', { class: 'tearhead__name', text: c.name }),
      h('p', { class: 'tearhead__meta', text: `${c.sector} · ${c.stage} · ${c.hq}` }),
    ]),
    h('dl', { class: 'factlist' }, [
      h('div', {}, [h('dt', { text: 'Ownership' }), h('dd', { text: Fmt.pct(c.ownership) })]),
      h('div', {}, [h('dt', { text: 'Invested' }), h('dd', { text: Fmt.millions(c.invested) })]),
      h('div', {}, [h('dt', { text: 'Carrying value' }), h('dd', { text: Fmt.millions(c.carryingValue) })]),
      h('div', {}, [h('dt', { text: 'First investment' }), h('dd', { text: Fmt.date(c.firstInvestment) })]),
      h('div', {}, [h('dt', { text: 'Board' }), h('dd', { text: c.boardSeat })]),
    ]),
  ]));

  host.append(h('div', { class: 'grid grid--stats' }, [
    statTile({
      hero: true,
      label: 'Revenue (LTM)',
      value: Fmt.millions(r),
      delta: `${Fmt.signedPct(growth)} year on year`,
      deltaTone: growth >= 0 ? 'good' : 'bad',
      sparkValues: win(c.series.revenue),
    }),
    statTile({
      label: 'Gross margin (LTM)',
      value: Fmt.pct(marginPct(ltm(c.series.grossProfit), r)),
      note: `${Fmt.millions(ltm(c.series.grossProfit))} gross profit`,
    }),
    statTile({
      label: 'EBITDA (LTM)',
      value: Fmt.millions(ltm(c.series.ebitda)),
      note: `${Fmt.pct(marginPct(ltm(c.series.ebitda), r))} margin`,
    }),
    statTile({
      label: 'Cash at quarter end',
      value: Fmt.millions(last(c.series.cash), 2),
      note: monthlyBurn(c.series.cash) > 0
        ? `${Fmt.money(monthlyBurn(c.series.cash))} net monthly burn`
        : 'Cash generative in the quarter',
    }),
    statTile({ label: 'Headcount', value: Fmt.count(last(c.series.headcount)), sparkValues: win(c.series.headcount) }),
  ]));

  host.append(h('div', { class: 'grid grid--3' }, [
    h('div', { class: 'panel' }, [
      h('div', { class: 'panel__head' }, [h('h3', { class: 'panel__title', text: 'Runway' })]),
      meter('Months of runway at the current burn', Math.min(Number.isFinite(months) ? months : 36, 36), 36, {
        tone: runwayTone(months) === 'critical' ? 'critical' : runwayTone(months) === 'good' ? 'accent' : 'warning',
        valueText: Number.isFinite(months) ? Fmt.months(months) : 'No burn this quarter',
      }),
      statusMark(runwayTone(months), runwayTone(months) === 'critical'
        ? 'Below six months — escalate to the board'
        : runwayTone(months) === 'serious' ? 'Under twelve months — funding plan required'
        : runwayTone(months) === 'warning' ? 'Under eighteen months — monitor'
        : 'Comfortable at the current burn'),
    ]),
    h('div', { class: 'panel' }, [
      h('div', { class: 'panel__head' }, [h('h3', { class: 'panel__title', text: `${DATA.meta.currentPeriod} return` })]),
      statusMark(REPORTING_TONE[c.reporting.status], REPORTING_LABEL[c.reporting.status]),
      h('p', { class: 'panel__sub', text: c.reporting.submitted
        ? `Submitted ${Fmt.date(c.reporting.submitted)} against a due date of ${Fmt.date(DATA.meta.dueDate)}.`
        : `Nothing received. Due ${Fmt.date(DATA.meta.dueDate)}.` }),
    ]),
    h('div', { class: 'panel' }, [
      h('div', { class: 'panel__head' }, [h('h3', { class: 'panel__title', text: 'Customers' })]),
      statTile({ bare: true, label: 'Active customers, sites or contracts', value: Fmt.count(last(c.series.customers)), sparkValues: win(c.series.customers) }),
    ]),
  ]));

  host.append(h('div', { class: 'grid grid--2' }, [
    panel('Revenue, gross profit and EBITDA', `${c.name}, £m by quarter`, lineChart({
      categories: ps,
      series: [
        { name: 'Revenue', values: win(c.series.revenue), color: seriesColour(0) },
        { name: 'Gross profit', values: win(c.series.grossProfit), color: seriesColour(1) },
        { name: 'EBITDA', values: win(c.series.ebitda), color: seriesColour(2) },
      ],
      format: (v) => Fmt.millions(v, 2),
      yFormat: (v) => (v / 1000).toFixed(1),
      tableCaption: `${c.name} trading by quarter, £m`,
      ariaLabel: `${c.name} revenue, gross profit and EBITDA by quarter`,
    })),
    panel('Cash at quarter end', `${c.name}, £m`, lineChart({
      categories: ps,
      series: [{ name: 'Cash', values: win(c.series.cash), color: seriesColour(0) }],
      format: (v) => Fmt.millions(v, 2),
      yFormat: (v) => (v / 1000).toFixed(1),
      tableCaption: `${c.name} cash at quarter end, £m`,
      ariaLabel: `${c.name} cash at quarter end by quarter`,
    })),
    panel('Headcount', `${c.name}, full-time equivalents`, columnChart({
      categories: ps,
      values: win(c.series.headcount),
      color: seriesColour(0),
      seriesName: 'Headcount',
      format: Fmt.count,
      tableCaption: `${c.name} headcount by quarter`,
      ariaLabel: `${c.name} headcount by quarter`,
    })),
    panel('Management commentary', `Submitted with the ${DATA.meta.currentPeriod} return`, [
      h('blockquote', { class: 'callout' }, [
        h('p', { text: c.commentary }),
        h('cite', { text: `${c.name} — ${DATA.meta.currentPeriod}` }),
      ]),
    ]),
  ]));
}

/* ============================================================ benchmarks == */

function renderBenchmarks() {
  const host = slot('benchmarks');
  host.textContent = '';
  const cs = activeCompanies();
  const c = currentCompany();
  if (cs.length < 2) {
    host.append(h('p', { text: 'Benchmarking needs at least two companies in scope. Widen the sector filter.' }));
    return;
  }

  const rows = cs.map((co) => ({
    id: co.id,
    label: co.name,
    value: Math.round((ltmGrowth(co.series.revenue) || 0) * 10) / 10,
    margin: marginPct(ltm(co.series.ebitda), ltm(co.series.revenue)),
  })).sort((a, b) => b.value - a.value);

  /* Emphasis, not a value ramp: the selected company takes slot 1, the cohort
     recedes to muted ink. Colour follows the entity, never its rank. */
  const s1 = getComputedStyle(document.documentElement).getPropertyValue('--s1').trim();
  const faint = getComputedStyle(document.documentElement).getPropertyValue('--ink-faint').trim();
  const barRows = rows.map((r) => ({
    ...r,
    color: r.id === (c && c.id) ? s1 : faint,
    note: r.id === (c && c.id) ? 'Selected company' : null,
  }));

  const sorted = [...rows].map((r) => r.value).sort((a, b) => a - b);
  const quantile = (p) => {
    const pos = (sorted.length - 1) * p;
    const lo = Math.floor(pos);
    const hi = Math.ceil(pos);
    return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
  };
  const q1 = quantile(0.25);
  const median = quantile(0.5);
  const q3 = quantile(0.75);

  const bandOf = (v) => (v >= q3 ? 4 : v >= median ? 3 : v >= q1 ? 2 : 1);
  const bandLabel = ['Bottom quartile', 'Third quartile', 'Second quartile', 'Top quartile'];

  host.append(section(
    'Cohort',
    `Quartiles are calculated across the ${cs.length} companies currently in scope, not against an external index.`,
    h('div', { class: 'grid grid--stats' }, [
      statTile({
        hero: true,
        label: c ? `${c.name} revenue growth (LTM)` : 'Revenue growth',
        value: Fmt.signedPct(ltmGrowth(c.series.revenue)),
        note: `${bandLabel[bandOf(ltmGrowth(c.series.revenue)) - 1]} of the cohort`,
      }),
      statTile({ label: 'Cohort top quartile', value: Fmt.signedPct(q3), note: 'Revenue growth, LTM' }),
      statTile({ label: 'Cohort median', value: Fmt.signedPct(median), note: 'Revenue growth, LTM' }),
      statTile({ label: 'Cohort bottom quartile', value: Fmt.signedPct(q1), note: 'Revenue growth, LTM' }),
    ]),
  ));

  /* The quartile bands themselves are ordered, so they take the ordinal ramp. */
  const ordLegend = h('div', { class: 'legend' });
  const ordSteps = ['--ord-1', '--ord-2', '--ord-3', '--ord-4'];
  const bandBounds = [
    `below ${Fmt.signedPct(q1)}`,
    `${Fmt.signedPct(q1)} to ${Fmt.signedPct(median)}`,
    `${Fmt.signedPct(median)} to ${Fmt.signedPct(q3)}`,
    `${Fmt.signedPct(q3)} and above`,
  ];
  bandLabel.forEach((lbl, i) => {
    ordLegend.append(h('span', { class: 'legend__item' }, [
      h('span', {
        class: 'legend__key legend__key--rect',
        style: `background:${getComputedStyle(document.documentElement).getPropertyValue(ordSteps[i]).trim()}`,
      }),
      h('span', { text: `${lbl} — ${bandBounds[i]}` }),
    ]));
  });

  host.append(h('div', { class: 'grid grid--2' }, [
    panel('Revenue growth against the cohort', 'Trailing twelve months, year on year', [
      barChart({
        rows: barRows,
        format: (v) => Fmt.signedPct(v),
        seriesName: 'Revenue growth LTM',
        highlight: c && c.id,
        tableCaption: 'Revenue growth by company, trailing twelve months',
        ariaLabel: 'Revenue growth by company against the cohort',
      }),
      h('p', { class: 'section__note', text: 'The selected company is emphasised; the rest of the cohort is held back so the comparison reads at a glance.' }),
    ]),
    panel('Growth against profitability', 'Each point is one company in scope', [
      scatterChart({
        points: cs.map((co) => ({
          id: co.id,
          label: co.name,
          x: ltmGrowth(co.series.revenue) || 0,
          y: marginPct(ltm(co.series.ebitda), ltm(co.series.revenue)) || 0,
        })),
        xLabel: 'Revenue growth LTM',
        yLabel: 'EBITDA margin LTM',
        highlight: c && c.id,
        tableCaption: 'Revenue growth and EBITDA margin by company',
        ariaLabel: 'Revenue growth against EBITDA margin by company',
      }),
    ]),
  ]));

  host.append(section('Quartile bands', 'Where each company falls on revenue growth.', [
    ordLegend,
    (() => {
      const t = h('table', { class: 'data' });
      t.append(h('caption', { text: 'Companies ranked on trailing twelve month revenue growth' }));
      t.append(h('thead', {}, [h('tr', {}, [
        h('th', { scope: 'col', text: 'Company' }),
        h('th', { scope: 'col', class: 'n', text: 'Revenue growth' }),
        h('th', { scope: 'col', class: 'n', text: 'EBITDA margin' }),
        h('th', { scope: 'col', text: 'Band' }),
      ])]));
      const tb = h('tbody');
      for (const r of rows) {
        tb.append(h('tr', {}, [
          h('th', { scope: 'row', text: r.label }),
          h('td', { class: 'n', text: Fmt.signedPct(r.value) }),
          h('td', { class: 'n', text: Fmt.pct(r.margin) }),
          h('td', {}, [h('span', { class: 'status' }, [
            h('span', {
              class: 'legend__key legend__key--rect',
              style: `background:${getComputedStyle(document.documentElement).getPropertyValue(ordSteps[bandOf(r.value) - 1]).trim()}`,
            }),
            h('span', { text: bandLabel[bandOf(r.value) - 1] }),
          ])]),
        ]));
      }
      t.append(tb);
      return h('div', { class: 'tablewrap' }, [t]);
    })(),
  ]));
}

/* ============================================================ collection == */

function renderCollection() {
  const host = slot('collection');
  host.textContent = '';
  const cs = activeCompanies();
  const ps = periods();
  const offset = DATA.periods.length - ps.length;

  const statesFor = (c) => DATA.submissions[c.id].slice(offset);
  const flat = cs.flatMap(statesFor);
  const received = flat.filter((s) => s === 'received').length;
  const late = flat.filter((s) => s === 'late').length;
  const outstanding = flat.filter((s) => s === 'outstanding').length;

  const thisPeriod = cs.map((c) => c.reporting.status);
  const chase = cs.filter((c) => c.reporting.status !== 'received');

  host.append(section(
    `Collection for ${DATA.meta.currentPeriod}`,
    `Returns were due ${Fmt.date(DATA.meta.dueDate)}.`,
    h('div', { class: 'grid grid--stats' }, [
      statTile({
        hero: true,
        label: 'Returns in on time',
        value: `${thisPeriod.filter((s) => s === 'received').length} of ${cs.length}`,
        note: `${thisPeriod.filter((s) => s === 'late').length} late, ${thisPeriod.filter((s) => s === 'outstanding').length} outstanding`,
      }),
      statTile({ label: 'On time across the window', value: Fmt.pct((received / flat.length) * 100, 0), note: `${ps.length} quarters, ${cs.length} companies` }),
      statTile({ label: 'Late returns in the window', value: String(late) }),
      statTile({ label: 'Never received', value: String(outstanding) }),
    ]),
  ));

  const onTimeByPeriod = ps.map((_, i) => cs.filter((c) => statesFor(c)[i] === 'received').length);
  const thisQuarterOk = thisPeriod.filter((s) => s === 'received').length;

  host.append(h('div', { class: 'grid grid--2' }, [
    panel('Returns in on time, by quarter', `Out of ${cs.length} requested each quarter`, columnChart({
      categories: ps,
      values: onTimeByPeriod,
      color: seriesColour(0),
      seriesName: 'Received on time',
      format: (v) => `${v} of ${cs.length}`,
      yFormat: (v) => String(v),
      tableCaption: 'Returns received on time by quarter',
      ariaLabel: 'Returns received on time by quarter',
    })),
    panel('This quarter', `Against a due date of ${Fmt.date(DATA.meta.dueDate)}`, [
      meter(`${DATA.meta.currentPeriod} returns in on time`, thisQuarterOk, cs.length, {
        tone: thisQuarterOk / cs.length >= 0.8 ? 'accent' : thisQuarterOk / cs.length >= 0.6 ? 'warning' : 'critical',
        valueText: `${thisQuarterOk} of ${cs.length}`,
      }),
      ...chase.map((c) => statusMark(REPORTING_TONE[c.reporting.status], `${c.name} — ${REPORTING_LABEL[c.reporting.status].toLowerCase()}`)),
      chase.length ? null : statusMark('good', 'Every company in scope has returned.'),
    ]),
  ]));

  /* The request grid — company against period, state in each cell. */
  const t = h('table', { class: 'data' });
  t.append(h('caption', { text: 'Quarterly returns requested and received. Each cell is one requested return.' }));
  const head = h('tr', {}, [h('th', { scope: 'col', text: 'Company' })]);
  for (const p of ps) head.append(h('th', { scope: 'col', text: p }));
  t.append(h('thead', {}, [head]));
  const tb = h('tbody');
  for (const c of cs) {
    const row = h('tr', {}, [h('th', { scope: 'row', text: c.name })]);
    statesFor(c).forEach((s) => {
      row.append(h('td', {}, [h('span', {
        class: `cellstate cellstate--${s}`,
        text: s === 'received' ? 'On time' : s === 'late' ? 'Late' : 'Missing',
      })]));
    });
    tb.append(row);
  }
  t.append(tb);
  host.append(section('Request grid', null, h('div', { class: 'reqgrid' }, [t])));

  /* Chase list. Nothing here sends anything — it drafts the words. */
  const chaseBody = [];
  if (!chase.length) {
    chaseBody.push(h('p', { class: 'section__note', text: 'Every company in scope has returned this quarter.' }));
  } else {
    for (const c of chase) {
      const draft = h('div', { hidden: true });
      const btn = h('button', { class: 'btn', type: 'button', text: 'Draft a chaser' });
      btn.addEventListener('click', () => {
        const open = draft.hidden;
        draft.hidden = !open;
        btn.textContent = open ? 'Hide draft' : 'Draft a chaser';
        if (open && !draft.childElementCount) {
          draft.append(
            h('p', { class: 'formfield__hint', text: 'Nothing is sent from this screen. Copy the text into your own mail client.' }),
            h('textarea', {
              rows: '8', readonly: true,
              style: 'width:100%;font:inherit;font-size:12.5px;color:var(--ink);background:transparent;border:1px solid var(--rule);border-radius:2px;padding:10px;resize:vertical',
              text: `Subject: ${DATA.meta.currentPeriod} reporting pack — ${c.name}\n\n`
                + `We have not yet received your ${DATA.meta.currentPeriod} return, which was due on ${Fmt.date(DATA.meta.dueDate)}.\n\n`
                + 'The board reviews the portfolio on a fixed cycle and your figures are needed to complete that pack. '
                + 'Please confirm a submission date by return, or tell us what is holding it up so we can help.\n\n'
                + 'Debrett’s advisory team',
            }),
          );
        }
      });
      chaseBody.push(h('div', { class: 'panel' }, [
        h('div', { class: 'panel__head' }, [
          h('h3', { class: 'panel__title', text: c.name }),
          statusMark(REPORTING_TONE[c.reporting.status], REPORTING_LABEL[c.reporting.status]),
        ]),
        h('p', { class: 'panel__sub', text: c.reporting.submitted
          ? `Arrived ${Fmt.date(c.reporting.submitted)}, after the due date.`
          : 'Nothing received for the quarter.' }),
        h('div', { class: 'formactions' }, [btn]),
        draft,
      ]));
    }
  }
  host.append(section('Chase list', 'Companies that have not returned on time this quarter.',
    h('div', { class: 'grid grid--2' }, chaseBody)));
}

/* ================================================================ submit == */

function renderSubmit() {
  const host = slot('submit');
  host.textContent = '';
  const c = currentCompany();
  if (!c) { host.append(h('p', { text: 'No company in scope for this filter.' })); return; }

  const priorIndex = DATA.periods.length - 2;
  const priorPeriod = DATA.periods[priorIndex];

  const form = h('form', { class: 'form', novalidate: true });
  form.append(
    h('p', { class: 'section__note', text:
      `${c.name} — return for ${DATA.meta.currentPeriod}, due ${Fmt.date(DATA.meta.dueDate)}. `
      + `Figures are compared against ${priorPeriod} as you type.` }),
  );

  const grid = h('div', { class: 'formgrid' });
  const inputs = {};
  for (const m of DATA.requestedMetrics) {
    const prior = c.series[m.key][priorIndex];
    const id = `m-${m.key}`;
    const variance = h('div', { class: 'formfield__variance' });
    const error = h('p', { class: 'formerror', hidden: true });
    const input = h('input', {
      id, name: m.key, type: 'number', step: 'any', inputmode: 'decimal',
      value: String(c.series[m.key][DATA.periods.length - 1]),
      'aria-describedby': `${id}-hint`,
    });
    const field = h('div', { class: 'formfield' }, [
      h('label', { for: id, text: `${m.label} (${m.unit})` }),
      input,
      h('p', { class: 'formfield__hint', id: `${id}-hint`, text: `${m.help} ${priorPeriod}: ${m.unit === '£000' ? Fmt.money(prior) : Fmt.count(prior)}.` }),
      variance,
      error,
    ]);
    const isMoney = m.unit === '£000';
    const update = () => {
      const v = Number(input.value);
      if (input.value === '' || Number.isNaN(v)) { variance.textContent = ''; return; }
      const change = v - prior;
      /* A percentage across a sign change says nothing useful, so a metric that
         can cross zero — EBITDA above all — reports the movement itself. */
      const usePct = prior > 0 && v > 0;
      const pctChange = usePct ? (change / prior) * 100 : null;
      variance.textContent = usePct
        ? `${Fmt.signedPct(pctChange)} against ${priorPeriod}`
        : `${change >= 0 ? '+' : '−'}${isMoney ? Fmt.money(Math.abs(change)) : Fmt.count(Math.abs(change))} against ${priorPeriod}`;
      const large = usePct ? Math.abs(pctChange) > 25 : Math.abs(change) > Math.abs(prior);
      variance.style.color = large ? 'var(--serious-ink)' : 'var(--ink-muted)';
    };
    input.addEventListener('input', update);
    update();
    inputs[m.key] = { input, field, error };
    grid.append(field);
  }
  form.append(h('fieldset', { style: 'border:0;padding:0;margin:0' }, [
    h('legend', { class: 'section__title', style: 'padding:0 0 12px', text: `Metrics for ${DATA.meta.currentPeriod}` }),
    grid,
  ]));

  const commentary = h('textarea', {
    id: 'm-commentary', rows: '5',
    placeholder: 'What moved in the quarter, what you expect next quarter, and anything the board should know.',
  });
  form.append(h('div', { class: 'formfield' }, [
    h('label', { for: 'm-commentary', text: 'Management commentary' }),
    commentary,
    h('p', { class: 'formfield__hint', text: 'Three or four sentences is enough. This is quoted directly in the board pack.' }),
  ]));

  form.append(h('div', { class: 'formfield' }, [
    h('label', { text: 'Supporting documents' }),
    h('div', { class: 'dropzone', text: 'Management accounts, cash forecast and cap table. File upload is not connected in this build.' }),
  ]));

  const toast = h('div', { class: 'toast', hidden: true, role: 'status' });
  const summary = h('div', { class: 'formerror', hidden: true, role: 'alert' });
  const submitBtn = h('button', { class: 'btn btn--primary', type: 'submit', text: 'Check and submit return' });
  form.append(summary, h('div', { class: 'formactions' }, [
    submitBtn,
    h('button', { class: 'btn', type: 'reset', text: 'Reset to last submitted' }),
  ]), toast);

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const problems = [];
    for (const m of DATA.requestedMetrics) {
      const { input, field, error } = inputs[m.key];
      const v = Number(input.value);
      let msg = null;
      if (input.value.trim() === '' || Number.isNaN(v)) msg = `${m.label} is required.`;
      else if (['revenue', 'grossProfit', 'cash', 'headcount', 'customers'].includes(m.key) && v < 0) {
        msg = `${m.label} cannot be negative.`;
      }
      field.classList.toggle('formfield--invalid', Boolean(msg));
      error.textContent = msg || '';
      error.hidden = !msg;
      if (msg) problems.push(msg);
    }
    const rev = Number(inputs.revenue.input.value);
    const gp = Number(inputs.grossProfit.input.value);
    const eb = Number(inputs.ebitda.input.value);
    if (!Number.isNaN(rev) && !Number.isNaN(gp) && gp > rev) {
      problems.push('Gross profit cannot exceed revenue.');
      inputs.grossProfit.field.classList.add('formfield--invalid');
      inputs.grossProfit.error.textContent = 'Gross profit cannot exceed revenue.';
      inputs.grossProfit.error.hidden = false;
    }
    if (!Number.isNaN(gp) && !Number.isNaN(eb) && eb > gp) {
      problems.push('EBITDA cannot exceed gross profit.');
      inputs.ebitda.field.classList.add('formfield--invalid');
      inputs.ebitda.error.textContent = 'EBITDA cannot exceed gross profit.';
      inputs.ebitda.error.hidden = false;
    }

    if (problems.length) {
      summary.hidden = false;
      summary.textContent = `${problems.length} ${problems.length === 1 ? 'field needs' : 'fields need'} attention before this return can go in.`;
      toast.hidden = true;
      return;
    }
    summary.hidden = true;
    toast.textContent = '';
    toast.append(statusMark('good', 'Return passed every check.'));
    toast.append(h('span', { text: 'No submission endpoint is connected in this build, so nothing has been sent.' }));
    toast.hidden = false;
  });

  host.append(section(`Quarterly return — ${c.name}`, 'The company’s own screen. Everything above the metrics is pre-filled from the last return.', form));
}

/* ============================================================ board pack == */

function sheetFooter(title, page) {
  return h('footer', { class: 'sheet__footer' }, [
    h('span', { text: title }),
    /* Drop the approved crown mark in here — never redrawn, recoloured or cropped. */
    h('span', { class: 'crownmark', 'data-asset': 'crown-mark', text: 'crown mark' }),
    h('span', { text: `DEBRETTS.COM / ${page}` }),
  ]);
}

function renderBoardPack() {
  const host = slot('boardpack');
  host.textContent = '';
  const cs = activeCompanies();
  const title = `Portfolio review — ${DATA.meta.currentPeriod}`;

  const rev = aggregate('revenue');
  const ebitda = aggregate('ebitda');
  /* Why a company is on the exceptions page, in the order the board cares. */
  const exceptionReason = (co) => {
    const months = runwayMonths(co.series.cash);
    if (months < 12) return { tone: runwayTone(months), text: `${Fmt.months(months)} of runway` };
    if (co.reporting.status !== 'received') {
      return { tone: REPORTING_TONE[co.reporting.status], text: REPORTING_LABEL[co.reporting.status] };
    }
    if ((ltmGrowth(co.series.revenue) || 0) < 0) {
      return { tone: 'warning', text: `Revenue ${Fmt.signedPct(ltmGrowth(co.series.revenue))} year on year` };
    }
    return null;
  };
  const exceptions = cs.filter((co) => exceptionReason(co));

  host.append(h('div', { class: 'formactions noprint', style: 'margin-bottom:4px' }, [
    h('button', { class: 'btn btn--primary', type: 'button', text: 'Print or save as PDF', onclick: () => window.print() }),
    h('p', { class: 'section__note', text: 'A4 landscape, 297 × 210mm with 9.5mm margins, per the Debrett’s page standard.' }),
  ]));

  const sheets = h('div', { class: 'sheets' });

  /* Cover — navy, per the brand standard for covers and dividers. */
  sheets.append(h('article', { class: 'sheet sheet--cover' }, [
    h('div', {}, [
      h('p', { class: 'eyebrow', text: 'Debrett’s portfolio reporting' }),
      h('p', { class: 'covertitle display', style: 'margin-top:12mm', text: title }),
    ]),
    h('div', {}, [
      h('p', { style: 'font-size:13px', text: `Prepared for the board · ${Fmt.date(DATA.meta.asOf)}` }),
      h('p', { style: 'font-size:13px;margin-top:4px', text: `${cs.length} portfolio companies · figures in pounds sterling` }),
    ]),
    sheetFooter(title, '01'),
  ]));

  /* Summary page */
  sheets.append(h('article', { class: 'sheet' }, [
    h('div', { class: 'sheet__body' }, [
      h('p', { class: 'eyebrow', text: 'Section one' }),
      h('h3', { class: 'panel__title', style: 'font-size:24px', text: 'Portfolio summary' }),
      h('div', { class: 'grid grid--stats' }, [
        statTile({ label: 'Revenue (LTM)', value: Fmt.millions(ltm(rev)), delta: `${Fmt.signedPct(ltmGrowth(rev))} year on year`, deltaTone: ltmGrowth(rev) >= 0 ? 'good' : 'bad' }),
        statTile({ label: 'EBITDA (LTM)', value: Fmt.millions(ltm(ebitda)) }),
        statTile({ label: 'Invested', value: Fmt.millions(sum(cs.map((x) => x.invested))) }),
        statTile({ label: 'Carrying value', value: Fmt.millions(sum(cs.map((x) => x.carryingValue))) }),
        statTile({ label: 'Returns in', value: `${cs.filter((x) => x.reporting.status === 'received').length} of ${cs.length}` }),
      ]),
      (() => {
        const t = h('table', { class: 'data' });
        t.append(h('thead', {}, [h('tr', {}, [
          h('th', { scope: 'col', text: 'Company' }),
          h('th', { scope: 'col', class: 'n', text: 'Revenue LTM' }),
          h('th', { scope: 'col', class: 'n', text: 'YoY' }),
          h('th', { scope: 'col', class: 'n', text: 'EBITDA margin' }),
          h('th', { scope: 'col', class: 'n', text: 'Runway' }),
          h('th', { scope: 'col', text: 'Return' }),
        ])]));
        const tb = h('tbody');
        for (const co of cs) {
          const r = ltm(co.series.revenue);
          tb.append(h('tr', {}, [
            h('th', { scope: 'row', text: co.name }),
            h('td', { class: 'n', text: Fmt.millions(r) }),
            h('td', { class: 'n', text: Fmt.signedPct(ltmGrowth(co.series.revenue)) }),
            h('td', { class: 'n', text: Fmt.pct(marginPct(ltm(co.series.ebitda), r)) }),
            h('td', { class: 'n', text: Fmt.months(runwayMonths(co.series.cash)) }),
            h('td', {}, [statusMark(REPORTING_TONE[co.reporting.status], REPORTING_LABEL[co.reporting.status])]),
          ]));
        }
        t.append(tb);
        return h('div', { class: 'tablewrap' }, [t]);
      })(),
    ]),
    sheetFooter(title, '02'),
  ]));

  /* Exceptions page */
  sheets.append(h('article', { class: 'sheet' }, [
    h('div', { class: 'sheet__body' }, [
      h('p', { class: 'eyebrow', text: 'Section two' }),
      h('h3', { class: 'panel__title', style: 'font-size:24px', text: 'Matters for the board' }),
      exceptions.length
        ? h('div', { class: 'grid grid--2' }, exceptions.map((co) => h('div', { class: 'panel' }, [
          h('div', { class: 'panel__head' }, [
            h('h4', { class: 'panel__title', style: 'font-size:15px', text: co.name }),
            statusMark(exceptionReason(co).tone, exceptionReason(co).text),
          ]),
          h('p', { style: 'font-size:12px', text: co.commentary }),
        ])))
        : h('p', { text: 'No company in scope met an exception test this quarter.' }),
    ]),
    sheetFooter(title, '03'),
  ]));

  host.append(sheets);
}

/* =============================================================== routing == */

const VIEWS = {
  portfolio: { title: 'Portfolio', render: renderPortfolio, filters: ['window', 'sector'] },
  company: { title: 'Company tear sheet', render: renderCompany, filters: ['window', 'sector', 'company'] },
  benchmarks: { title: 'Benchmarks', render: renderBenchmarks, filters: ['window', 'sector', 'company'] },
  collection: { title: 'Data collection', render: renderCollection, filters: ['window', 'sector'] },
  submit: { title: 'Submit a return', render: renderSubmit, filters: ['sector', 'company'] },
  boardpack: { title: 'Board pack', render: renderBoardPack, filters: ['sector'] },
};

function go(view) {
  state.view = view;
  render();
}

function render() {
  const conf = VIEWS[state.view];

  $$('.navlink').forEach((b) => {
    const on = b.dataset.view === state.view;
    if (on) b.setAttribute('aria-current', 'page');
    else b.removeAttribute('aria-current');
  });
  $$('.view').forEach((v) => { v.hidden = v.dataset.view !== state.view; });

  slot('viewTitle').textContent = conf.title;
  const c = currentCompany();
  slot('viewMeta').textContent = state.view === 'company' || state.view === 'submit'
    ? `${c ? c.name : '—'} · as at ${Fmt.date(DATA.meta.asOf)}`
    : `${activeCompanies().length} companies · as at ${Fmt.date(DATA.meta.asOf)}`;

  /* Only show the filters a view actually honours. */
  $$('[data-filter]').forEach((el) => {
    el.closest('.field').hidden = !conf.filters.includes(el.dataset.filter);
  });

  $('[data-count="companies"]').textContent = String(activeCompanies().length);
  const outstanding = activeCompanies().filter((x) => x.reporting.status !== 'received').length;
  const badge = $('[data-count="outstanding"]');
  badge.textContent = outstanding ? String(outstanding) : '';

  conf.render();
}

/* ---------------------------------------------------------------- wiring -- */

function buildFilters() {
  const sectorSel = $('[data-filter="sector"]');
  sectorSel.append(h('option', { value: 'all', text: 'All sectors' }));
  for (const s of [...new Set(DATA.companies.map((c) => c.sector))].sort()) {
    sectorSel.append(h('option', { value: s, text: s }));
  }
  syncCompanyOptions();

  $('[data-filter="window"]').addEventListener('change', (e) => {
    state.windowN = Number(e.target.value);
    render();
  });
  sectorSel.addEventListener('change', (e) => {
    state.sector = e.target.value;
    syncCompanyOptions();
    render();
  });
  $('[data-filter="company"]').addEventListener('change', (e) => {
    state.companyId = e.target.value;
    render();
  });
}

function syncCompanyOptions() {
  const sel = $('[data-filter="company"]');
  sel.textContent = '';
  const cs = activeCompanies();
  for (const c of cs) sel.append(h('option', { value: c.id, text: c.name }));
  if (!cs.some((c) => c.id === state.companyId)) state.companyId = cs.length ? cs[0].id : null;
  if (state.companyId) sel.value = state.companyId;
}

function boot() {
  $$('.navlink').forEach((b) => b.addEventListener('click', () => go(b.dataset.view)));
  buildFilters();

  $('[data-action="theme"]').addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const showing = current || (prefersDark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', showing === 'dark' ? 'light' : 'dark');
    render(); /* charts read their colours from the tokens, so re-draw */
  });

  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (!document.documentElement.getAttribute('data-theme')) render();
  });

  if (DATA.meta.isSample) {
    slot('sampleChip').textContent = 'Sample data — not Debrett’s portfolio';
  }

  render();
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
else boot();
