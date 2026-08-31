/* Behavioural checks against the built page.
 *
 *   python3 build.py && node test/interaction.mjs
 *
 * Drives dist/debretts-portfolio-reporting.html in Chromium and asserts the
 * things a static read of the source cannot: that tooltips open, that keyboard
 * focus gives the same readout as hover, that the table twins reveal, that the
 * filters scope every view, that the return form rejects an impossible figure
 * and never claims to have sent anything, and that the page never scrolls
 * sideways. Exits non-zero if any check fails.
 */
// Resolve Playwright from the project or from a global install.
const { chromium } = await import('playwright').catch(async () => {
  const { execSync } = await import('node:child_process');
  const root = execSync('npm root -g', { encoding: 'utf8' }).trim();
  return import(`${root}/playwright/index.mjs`);
});
const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
const page = await ctx.newPage();
const errs = [];
page.on('pageerror', e => errs.push('pageerror: ' + e.message));
await page.goto('file:///home/user/financial-services/portfolio-reporting-dashboard/dist/debretts-portfolio-reporting.html');
await page.waitForTimeout(600);
const ok = [];

// 1. line chart crosshair tooltip
const lineHit = page.locator('.view[data-view="portfolio"] .chart__hit').first();
const lb = await lineHit.boundingBox();
await page.mouse.move(lb.x + lb.width / 2, lb.y + lb.height / 2);
await page.waitForTimeout(200);
ok.push(['line tooltip open', await page.locator('.view[data-view="portfolio"] .tooltip[data-open="true"]').count() > 0]);
ok.push(['tooltip lists 3 series', await page.locator('.view[data-view="portfolio"] .tooltip[data-open="true"] .tooltip__row').count() >= 3]);

// 2. keyboard on the chart hit area
await lineHit.focus();
await page.keyboard.press('ArrowLeft');
await page.waitForTimeout(150);
ok.push(['keyboard readout', await page.locator('.view[data-view="portfolio"] .tooltip[data-open="true"]').count() > 0]);

// 3. table twin toggle
const toggle = page.locator('.view[data-view="portfolio"] .toggle').first();
await toggle.click();
await page.waitForTimeout(150);
ok.push(['table twin opens', await page.locator('.view[data-view="portfolio"] .chart__foot').first().locator('xpath=following-sibling::div[1]').isVisible()]);
ok.push(['toggle label flips', (await toggle.textContent()) === 'Hide table']);

// 4. column chart per-bar tooltip
await page.click('.navlink[data-view="company"]');
await page.waitForTimeout(300);
const bars = page.locator('.view[data-view="company"] svg rect[role="img"]');
ok.push(['column hit areas', await bars.count() >= 8]);
// a transparent hit rect is hoverable by a pointer but "invisible" to Playwright,
// so drive the real mouse to its box instead of using .hover()
await bars.first().scrollIntoViewIfNeeded();
await page.waitForTimeout(150);
const box = await bars.first().boundingBox();
await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
await page.waitForTimeout(200);
ok.push(['column tooltip', await page.locator('.view[data-view="company"] .tooltip[data-open="true"]').count() > 0]);

// 5. sector filter scopes everything
await page.click('.navlink[data-view="portfolio"]');
await page.selectOption('[data-filter="sector"]', 'Software & data');
await page.waitForTimeout(300);
const rows = await page.locator('.view[data-view="portfolio"] .section >> nth=-1').locator('> .tablewrap table.data tbody tr').count();
ok.push(['sector filter narrows table to 1', rows === 1]);
ok.push(['nav count follows', (await page.locator('[data-count="companies"]').textContent()) === '1']);
await page.selectOption('[data-filter="sector"]', 'all');
await page.waitForTimeout(200);

// 6. period window scopes the charts
await page.selectOption('[data-filter="window"]', '4');
await page.waitForTimeout(300);
await page.locator('.view[data-view="portfolio"] .toggle').first().click();
await page.waitForTimeout(150);
const plotted = await page.locator('.view[data-view="portfolio"] .chart__foot').first().locator('xpath=following-sibling::div[1]').locator('tbody tr').count();
ok.push(['four-quarter window plots 4 rows', plotted === 4]);
await page.selectOption('[data-filter="window"]', '8');
await page.waitForTimeout(200);

// 7. company drill-through from the table
await page.click('.view[data-view="portfolio"] .linkcell >> nth=2');
await page.waitForTimeout(300);
ok.push(['drill-through switches view', await page.locator('.view[data-view="company"]').isVisible()]);
ok.push(['drill-through picks the company', (await page.locator('.tearhead__name').textContent()).includes('Ardenne')]);

// 8. submit form validation
await page.click('.navlink[data-view="submit"]');
await page.waitForTimeout(300);
await page.fill('#m-grossProfit', '999999');
await page.click('button[type="submit"]');
await page.waitForTimeout(200);
ok.push(['gross profit > revenue rejected', await page.locator('.formfield--invalid').count() > 0]);
await page.fill('#m-grossProfit', '2995');
await page.click('button[type="submit"]');
await page.waitForTimeout(200);
ok.push(['valid return passes', await page.locator('.toast:not([hidden])').count() === 1]);
ok.push(['no false send claim', (await page.locator('.toast').textContent()).includes('nothing has been sent')]);

// 9. chaser draft
await page.click('.navlink[data-view="collection"]');
await page.waitForTimeout(300);
await page.locator('.view[data-view="collection"] button', { hasText: 'Draft a chaser' }).first().click();
await page.waitForTimeout(200);
ok.push(['chaser draft opens', await page.locator('textarea[readonly]').first().isVisible()]);

// 10. theme toggle re-renders charts with new tokens
await page.click('.navlink[data-view="portfolio"]');
await page.waitForTimeout(200);
const before = await page.locator('.view[data-view="portfolio"] .chart svg path[stroke]').first().getAttribute('stroke');
await page.click('[data-action="theme"]');
await page.waitForTimeout(300);
const after = await page.locator('.view[data-view="portfolio"] .chart svg path[stroke]').first().getAttribute('stroke');
ok.push(['theme toggle restyles marks', before !== after]);

// 11. no horizontal page scroll
const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
ok.push(['no page-level horizontal scroll', overflow <= 0]);

for (const [name, pass] of ok) console.log((pass ? 'PASS  ' : 'FAIL  ') + name);
console.log(errs.length ? errs.join('\n') : 'no page errors');
await browser.close();
const failed = ok.filter(([, pass]) => !pass).length + errs.length;
if (failed) { console.error(`${failed} check(s) failed`); process.exit(1); }
