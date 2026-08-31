/* ==========================================================================
   Chart library — hand-built SVG, no dependencies.

   Mark specs are fixed across every chart in the application:
     line          2px, round cap and join
     area          series hue at 10% — a wash, never a block
     marker        r >= 4 with a 2px ring in the surface colour
     column / bar  <= 24px thick, 4px rounded data-end, square at the baseline,
                   2px surface gap between neighbours
     grid / axis   solid hairlines, one step off the surface

   Every chart ships a hover and keyboard-focus readout and a table twin, so no
   value is reachable only by pointing at it.
   ========================================================================== */

const NS = 'http://www.w3.org/2000/svg';

/* ------------------------------------------------------------ formatting -- */

const Fmt = {
  /* £ thousands in, readable money out */
  money(k, { dp } = {}) {
    if (k === null || k === undefined || Number.isNaN(k)) return '—';
    const sign = k < 0 ? '−' : '';
    const a = Math.abs(k);
    if (a >= 1000) return `${sign}£${(a / 1000).toFixed(dp === undefined ? (a >= 10000 ? 1 : 2) : dp)}m`;
    return `${sign}£${Math.round(a).toLocaleString('en-GB')}k`;
  },
  millions(k, dp = 1) {
    if (k === null || k === undefined || Number.isNaN(k)) return '—';
    return `${k < 0 ? '−' : ''}£${(Math.abs(k) / 1000).toFixed(dp)}m`;
  },
  count(n) {
    if (n === null || n === undefined || Number.isNaN(n)) return '—';
    return Math.round(n).toLocaleString('en-GB');
  },
  pct(n, dp = 1) {
    if (n === null || n === undefined || !Number.isFinite(n)) return '—';
    return `${n < 0 ? '−' : ''}${Math.abs(n).toFixed(dp)}%`;
  },
  signedPct(n, dp = 1) {
    if (n === null || n === undefined || !Number.isFinite(n)) return '—';
    return `${n > 0 ? '+' : n < 0 ? '−' : ''}${Math.abs(n).toFixed(dp)}%`;
  },
  months(n) {
    if (!Number.isFinite(n)) return 'Cash generative';
    if (n > 60) return 'Over 60 mths';
    return `${n.toFixed(1)} mths`;
  },
  date(iso) {
    if (!iso) return '—';
    const d = new Date(`${iso}T00:00:00Z`);
    const months = ['JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
      'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'];
    return `${d.getUTCDate()} ${months[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
  },
};

/* ----------------------------------------------------------------- utils -- */

function svgEl(tag, attrs = {}) {
  const node = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v !== null && v !== undefined) node.setAttribute(k, String(v));
  }
  return node;
}

function h(tag, attrs = {}, children = []) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === 'class') node.className = v;
    else if (k === 'text') node.textContent = v;          // untrusted labels
    else if (k === 'html') node.innerHTML = v;            // authored markup only
    else if (k.startsWith('on') && typeof v === 'function') node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? '' : String(v));
  }
  for (const c of [].concat(children)) {
    if (c === null || c === undefined) continue;
    node.append(c.nodeType ? c : document.createTextNode(String(c)));
  }
  return node;
}

/* Round tick values — 1 / 2 / 2.5 / 5 / 10 × 10^n, always including zero. */
function niceScale(min, max, target = 5) {
  if (min === max) { min -= 1; max += 1; }
  const lo = Math.min(0, min);
  const hi = Math.max(0, max);
  const raw = (hi - lo) / target;
  const mag = Math.pow(10, Math.floor(Math.log10(raw)));
  const norm = raw / mag;
  const step = (norm <= 1 ? 1 : norm <= 2 ? 2 : norm <= 2.5 ? 2.5 : norm <= 5 ? 5 : 10) * mag;
  const start = Math.floor(lo / step) * step;
  const end = Math.ceil(hi / step) * step;
  const ticks = [];
  for (let v = start; v <= end + step / 1000; v += step) ticks.push(Math.round(v * 1e6) / 1e6);
  return { min: start, max: end, ticks };
}

const cssVar = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

/* Attach a tooltip element to a chart container and return a controller. */
function makeTooltip(container) {
  const tip = h('div', { class: 'tooltip', role: 'status', 'aria-live': 'polite' });
  container.append(tip);
  return {
    node: tip,
    show(x, y, title, rows) {
      tip.textContent = '';
      tip.append(h('div', { class: 'tooltip__title', text: title }));
      for (const r of rows) {
        tip.append(h('div', { class: 'tooltip__row' }, [
          r.color ? h('span', { class: 'tooltip__key', style: `background:${r.color}` }) : null,
          h('span', { class: 'tooltip__name', text: r.name }),
          h('span', { class: 'tooltip__val', text: r.value }),
        ]));
      }
      tip.dataset.open = 'true';
      const cw = container.clientWidth;
      const tw = tip.offsetWidth;
      let left = x + 14;
      if (left + tw > cw) left = Math.max(0, x - tw - 14);
      tip.style.left = `${left}px`;
      tip.style.top = `${Math.max(0, y - tip.offsetHeight - 10)}px`;
    },
    hide() { tip.dataset.open = 'false'; },
  };
}

/* Map a pointer event to viewBox coordinates (uniform scale, so proportional). */
function toViewBox(svg, evt, vbWidth, vbHeight) {
  const r = svg.getBoundingClientRect();
  return {
    x: ((evt.clientX - r.left) / r.width) * vbWidth,
    y: ((evt.clientY - r.top) / r.height) * vbHeight,
  };
}

/* A legend is always present for two or more series; one series needs none. */
function buildLegend(series, kind = 'line') {
  if (series.length < 2) return null;
  const wrap = h('div', { class: 'legend' });
  for (const s of series) {
    wrap.append(h('span', { class: 'legend__item' }, [
      h('span', { class: `legend__key${kind === 'rect' ? ' legend__key--rect' : ''}`, style: `background:${s.color}` }),
      h('span', { text: s.name }),
    ]));
  }
  return wrap;
}

/* The table twin — every charted value, reachable without a pointer. */
function buildTable(categories, series, format, caption) {
  const wrap = h('div', { class: 'tablewrap', hidden: true });
  const table = h('table', { class: 'data' });
  table.append(h('caption', { text: caption }));
  const head = h('tr', {}, [h('th', { scope: 'col', text: 'Period' })]);
  for (const s of series) head.append(h('th', { scope: 'col', class: 'n', text: s.name }));
  table.append(h('thead', {}, [head]));
  const body = h('tbody');
  categories.forEach((cat, i) => {
    const row = h('tr', {}, [h('th', { scope: 'row', text: cat })]);
    for (const s of series) row.append(h('td', { class: 'n', text: format(s.values[i]) }));
    body.append(row);
  });
  table.append(body);
  wrap.append(table);
  return wrap;
}

function buildFoot(legend, tableWrap) {
  const foot = h('div', { class: 'chart__foot' });
  if (legend) foot.append(legend);
  if (tableWrap) {
    const btn = h('button', {
      class: 'toggle', type: 'button', text: 'Show table', 'aria-expanded': 'false',
    });
    btn.addEventListener('click', () => {
      const open = tableWrap.hidden;
      tableWrap.hidden = !open;
      btn.textContent = open ? 'Hide table' : 'Show table';
      btn.setAttribute('aria-expanded', String(open));
    });
    foot.append(btn);
  }
  return foot;
}

/* ============================================================ line chart == */
/*
   config: { categories, series:[{key,name,values,color}], format, yFormat,
             title, height, labelLast }
*/
function lineChart(config) {
  const {
    categories, series, height = 230, labelLast = true,
    format = Fmt.count, yFormat = (v) => v.toLocaleString('en-GB'),
    tableCaption = 'All plotted values',
  } = config;

  const W = 720;
  const H = height;
  const pad = { t: 14, r: labelLast ? 74 : 20, b: 30, l: 52 };
  const plotW = W - pad.l - pad.r;
  const plotH = H - pad.t - pad.b;

  const all = series.flatMap((s) => s.values);
  const scale = niceScale(Math.min(...all), Math.max(...all));
  const x = (i) => pad.l + (categories.length === 1 ? plotW / 2 : (i / (categories.length - 1)) * plotW);
  const y = (v) => pad.t + plotH - ((v - scale.min) / (scale.max - scale.min)) * plotH;

  const container = h('div', { class: 'chart' });
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': config.ariaLabel || tableCaption });

  /* grid — solid hairlines, recessive */
  const grid = svgEl('g', { class: 'chart__grid' });
  for (const t of scale.ticks) {
    grid.append(svgEl('line', { x1: pad.l, x2: pad.l + plotW, y1: y(t), y2: y(t) }));
    const label = svgEl('text', { class: 'chart__tick', x: pad.l - 8, y: y(t) + 3.5, 'text-anchor': 'end' });
    label.textContent = yFormat(t);
    grid.append(label);
  }
  svg.append(grid);

  /* zero line reads stronger than the grid where the scale crosses it */
  if (scale.min < 0 && scale.max > 0) {
    svg.append(svgEl('line', {
      x1: pad.l, x2: pad.l + plotW, y1: y(0), y2: y(0),
      stroke: cssVar('--axis'), 'stroke-width': 1,
    }));
  }

  /* x ticks — first, last and every other one between */
  const axis = svgEl('g', { class: 'chart__axis' });
  categories.forEach((cat, i) => {
    if (i !== 0 && i !== categories.length - 1 && i % 2 !== 0) return;
    const t = svgEl('text', {
      class: 'chart__tick', x: x(i), y: pad.t + plotH + 18,
      'text-anchor': i === 0 ? 'start' : i === categories.length - 1 ? 'end' : 'middle',
    });
    t.textContent = cat;
    axis.append(t);
  });
  svg.append(axis);

  /* one series → area wash under the line; several → lines only, no stacking */
  if (series.length === 1) {
    const s = series[0];
    const d = series[0].values.map((v, i) => `${i ? 'L' : 'M'}${x(i)} ${y(v)}`).join(' ');
    const base = Math.max(scale.min, Math.min(0, scale.max));
    svg.append(svgEl('path', {
      d: `${d} L${x(s.values.length - 1)} ${y(base)} L${x(0)} ${y(base)} Z`,
      fill: s.color, 'fill-opacity': 0.1, stroke: 'none',
    }));
  }

  for (const s of series) {
    svg.append(svgEl('path', {
      d: s.values.map((v, i) => `${i ? 'L' : 'M'}${x(i)} ${y(v)}`).join(' '),
      fill: 'none', stroke: s.color, 'stroke-width': 2,
      'stroke-linecap': 'round', 'stroke-linejoin': 'round',
    }));
    /* endpoint marker with a surface ring so overlaps stay legible */
    const li = s.values.length - 1;
    svg.append(svgEl('circle', {
      cx: x(li), cy: y(s.values[li]), r: 4.5,
      fill: s.color, stroke: cssVar('--surface'), 'stroke-width': 2,
    }));
  }

  /* direct-label the endpoints only, in text ink — never the series colour */
  if (labelLast) {
    const placed = [];
    for (const s of series) {
      const li = s.values.length - 1;
      let ly = y(s.values[li]) + 4;
      while (placed.some((p) => Math.abs(p - ly) < 13)) ly += 13;
      placed.push(ly);
      const t = svgEl('text', { class: 'chart__label', x: x(li) + 10, y: ly });
      t.textContent = format(s.values[li]);
      svg.append(t);
    }
  }

  /* crosshair + one readout listing every series at that x */
  const cross = svgEl('line', { class: 'chart__crosshair', y1: pad.t, y2: pad.t + plotH, opacity: 0 });
  svg.append(cross);
  const dots = series.map((s) => {
    const c = svgEl('circle', { r: 4.5, fill: s.color, stroke: cssVar('--surface'), 'stroke-width': 2, opacity: 0 });
    svg.append(c);
    return c;
  });

  const hit = svgEl('rect', { class: 'chart__hit', x: pad.l, y: pad.t, width: plotW, height: plotH, tabindex: 0 });
  svg.append(hit);
  const tip = makeTooltip(container);

  let focusIndex = categories.length - 1;
  const showAt = (i, clientPos) => {
    focusIndex = i;
    cross.setAttribute('x1', x(i));
    cross.setAttribute('x2', x(i));
    cross.setAttribute('opacity', 1);
    dots.forEach((d, si) => {
      d.setAttribute('cx', x(i));
      d.setAttribute('cy', y(series[si].values[i]));
      d.setAttribute('opacity', 1);
    });
    const r = svg.getBoundingClientRect();
    const px = clientPos ? clientPos.x : r.left + (x(i) / W) * r.width;
    const py = clientPos ? clientPos.y : r.top + (y(series[0].values[i]) / H) * r.height;
    const cr = container.getBoundingClientRect();
    tip.show(px - cr.left, py - cr.top, categories[i],
      series.map((s) => ({ color: s.color, name: s.name, value: format(s.values[i]) })));
  };
  const clear = () => {
    cross.setAttribute('opacity', 0);
    dots.forEach((d) => d.setAttribute('opacity', 0));
    tip.hide();
  };

  hit.addEventListener('pointermove', (e) => {
    const p = toViewBox(svg, e, W, H);
    const i = Math.max(0, Math.min(categories.length - 1,
      Math.round(((p.x - pad.l) / plotW) * (categories.length - 1))));
    showAt(i, { x: e.clientX, y: e.clientY });
  });
  hit.addEventListener('pointerleave', clear);
  hit.addEventListener('focus', () => showAt(focusIndex));
  hit.addEventListener('blur', clear);
  hit.addEventListener('keydown', (e) => {
    if (e.key !== 'ArrowLeft' && e.key !== 'ArrowRight') return;
    e.preventDefault();
    showAt(Math.max(0, Math.min(categories.length - 1, focusIndex + (e.key === 'ArrowRight' ? 1 : -1))));
  });

  container.append(svg);
  const table = buildTable(categories, series, format, tableCaption);
  return h('div', {}, [container, buildFoot(buildLegend(series, 'line'), table), table]);
}

/* ========================================================== column chart == */
/*  Single series of columns — the mark is the hit target, no crosshair. */
function columnChart(config) {
  const {
    categories, values, color, height = 200,
    format = Fmt.count, yFormat = (v) => v.toLocaleString('en-GB'),
    tableCaption = 'All plotted values', seriesName = 'Value',
  } = config;

  const W = 720;
  const H = height;
  const pad = { t: 14, r: 16, b: 30, l: 52 };
  const plotW = W - pad.l - pad.r;
  const plotH = H - pad.t - pad.b;
  const scale = niceScale(Math.min(...values), Math.max(...values));
  const band = plotW / categories.length;
  const barW = Math.min(24, band - 2 /* 2px surface gap between neighbours */);
  const y = (v) => pad.t + plotH - ((v - scale.min) / (scale.max - scale.min)) * plotH;
  const zeroY = y(Math.max(scale.min, Math.min(0, scale.max)));

  const container = h('div', { class: 'chart' });
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': config.ariaLabel || tableCaption });

  const grid = svgEl('g', { class: 'chart__grid' });
  for (const t of scale.ticks) {
    grid.append(svgEl('line', { x1: pad.l, x2: pad.l + plotW, y1: y(t), y2: y(t) }));
    const label = svgEl('text', { class: 'chart__tick', x: pad.l - 8, y: y(t) + 3.5, 'text-anchor': 'end' });
    label.textContent = yFormat(t);
    grid.append(label);
  }
  svg.append(grid);

  const tip = makeTooltip(container);

  categories.forEach((cat, i) => {
    const cx = pad.l + band * i + band / 2;
    const v = values[i];
    const top = Math.min(y(v), zeroY);
    const hgt = Math.max(1, Math.abs(y(v) - zeroY));
    /* 4px rounded data-end, square at the baseline */
    const r = Math.min(4, hgt);
    const up = v >= 0;
    const x0 = cx - barW / 2;
    const d = up
      ? `M${x0} ${top + hgt} L${x0} ${top + r} Q${x0} ${top} ${x0 + r} ${top} L${x0 + barW - r} ${top} Q${x0 + barW} ${top} ${x0 + barW} ${top + r} L${x0 + barW} ${top + hgt} Z`
      : `M${x0} ${top} L${x0} ${top + hgt - r} Q${x0} ${top + hgt} ${x0 + r} ${top + hgt} L${x0 + barW - r} ${top + hgt} Q${x0 + barW} ${top + hgt} ${x0 + barW} ${top + hgt - r} L${x0 + barW} ${top} Z`;
    const bar = svgEl('path', { d, fill: color, class: 'chart__mark' });
    svg.append(bar);

    /* hit area larger than the mark, and keyboard reachable */
    const hit = svgEl('rect', {
      x: pad.l + band * i, y: pad.t, width: band, height: plotH,
      fill: 'transparent', tabindex: 0, role: 'img',
      'aria-label': `${cat}: ${format(v)}`,
    });
    const show = (e) => {
      const cr = container.getBoundingClientRect();
      const br = svg.getBoundingClientRect();
      const px = e && e.clientX ? e.clientX - cr.left : (cx / W) * br.width + br.left - cr.left;
      const py = e && e.clientY ? e.clientY - cr.top : (top / H) * br.height + br.top - cr.top;
      bar.setAttribute('opacity', 0.82);
      tip.show(px, py, cat, [{ color, name: seriesName, value: format(v) }]);
    };
    const hide = () => { bar.removeAttribute('opacity'); tip.hide(); };
    hit.addEventListener('pointerenter', show);
    hit.addEventListener('pointermove', show);
    hit.addEventListener('pointerleave', hide);
    hit.addEventListener('focus', () => show());
    hit.addEventListener('blur', hide);
    svg.append(hit);
  });

  const axis = svgEl('g', { class: 'chart__axis' });
  categories.forEach((cat, i) => {
    if (i !== 0 && i !== categories.length - 1 && i % 2 !== 0) return;
    const t = svgEl('text', {
      class: 'chart__tick', x: pad.l + band * i + band / 2,
      y: pad.t + plotH + 18, 'text-anchor': 'middle',
    });
    t.textContent = cat;
    axis.append(t);
  });
  svg.append(axis);

  container.append(svg);
  const series = [{ name: seriesName, values, color }];
  const table = buildTable(categories, series, format, tableCaption);
  return h('div', {}, [container, buildFoot(null, table), table]);
}

/* ====================================================== horizontal bars ==== */
/*
   rows: [{ label, value, color, note }] — used for the benchmark bands, where
   colour carries an ordered position, and for plain nominal comparisons, where
   every bar takes slot 1.
*/
function barChart(config) {
  const {
    rows, format = Fmt.count, tableCaption = 'All plotted values',
    seriesName = 'Value', highlight = null, ordinalLegend = null,
  } = config;

  const W = 720;
  const rowH = 30;
  const pad = { t: 6, r: 96, b: 6, l: 168 };
  const H = pad.t + pad.b + rows.length * rowH;
  const plotW = W - pad.l - pad.r;
  const max = Math.max(...rows.map((r) => r.value), 0);
  const min = Math.min(...rows.map((r) => r.value), 0);
  const scale = niceScale(min, max);
  const x = (v) => pad.l + ((v - scale.min) / (scale.max - scale.min)) * plotW;

  const container = h('div', { class: 'chart' });
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': config.ariaLabel || tableCaption });
  const tip = makeTooltip(container);
  const zeroX = x(Math.max(scale.min, Math.min(0, scale.max)));

  rows.forEach((row, i) => {
    const yTop = pad.t + i * rowH + (rowH - 16) / 2;
    const barH = 16 - 2; /* 2px surface gap between neighbours */
    const w = Math.max(1, Math.abs(x(row.value) - zeroX));
    const x0 = Math.min(x(row.value), zeroX);
    const r = Math.min(4, w);
    const pos = row.value >= 0;
    const d = pos
      ? `M${x0} ${yTop} L${x0 + w - r} ${yTop} Q${x0 + w} ${yTop} ${x0 + w} ${yTop + r} L${x0 + w} ${yTop + barH - r} Q${x0 + w} ${yTop + barH} ${x0 + w - r} ${yTop + barH} L${x0} ${yTop + barH} Z`
      : `M${x0 + w} ${yTop} L${x0 + r} ${yTop} Q${x0} ${yTop} ${x0} ${yTop + r} L${x0} ${yTop + barH - r} Q${x0} ${yTop + barH} ${x0 + r} ${yTop + barH} L${x0 + w} ${yTop + barH} Z`;

    const bar = svgEl('path', { d, fill: row.color, class: 'chart__mark' });
    svg.append(bar);

    const label = svgEl('text', {
      class: 'chart__label', x: pad.l - 12, y: yTop + barH / 2 + 4, 'text-anchor': 'end',
      'font-weight': highlight && row.id === highlight ? 600 : 400,
    });
    label.textContent = row.label;
    svg.append(label);

    /* Values sit in a right-hand column rather than at each tip: with bars on
       both sides of zero, tip labels collide with the category names. */
    const val = svgEl('text', {
      class: 'chart__label', x: W - 8, y: yTop + barH / 2 + 4, 'text-anchor': 'end',
    });
    val.textContent = format(row.value);
    svg.append(val);

    const hit = svgEl('rect', {
      x: 0, y: pad.t + i * rowH, width: W, height: rowH, fill: 'transparent',
      tabindex: 0, role: 'img', 'aria-label': `${row.label}: ${format(row.value)}${row.note ? `, ${row.note}` : ''}`,
    });
    const show = (e) => {
      const cr = container.getBoundingClientRect();
      const br = svg.getBoundingClientRect();
      const px = e && e.clientX ? e.clientX - cr.left : br.left - cr.left + ((x0 + w) / W) * br.width;
      const py = e && e.clientY ? e.clientY - cr.top : br.top - cr.top + ((yTop) / H) * br.height;
      bar.setAttribute('opacity', 0.82);
      tip.show(px, py, row.label, [
        { color: row.color, name: seriesName, value: format(row.value) },
        ...(row.note ? [{ color: null, name: '', value: row.note }] : []),
      ]);
    };
    const hide = () => { bar.removeAttribute('opacity'); tip.hide(); };
    hit.addEventListener('pointerenter', show);
    hit.addEventListener('pointermove', show);
    hit.addEventListener('pointerleave', hide);
    hit.addEventListener('focus', () => show());
    hit.addEventListener('blur', hide);
    svg.append(hit);
  });

  container.append(svg);
  const table = buildTable(
    rows.map((r) => r.label),
    [{ name: seriesName, values: rows.map((r) => r.value), color: rows[0] ? rows[0].color : null }],
    format,
    tableCaption,
  );
  return h('div', {}, [container, buildFoot(ordinalLegend, table), table]);
}

/* ================================================================ scatter == */
/*
   Growth against margin. All-pairs colour separation caps this form at two
   series in the Debrett's palette, so it carries one series with the selected
   company emphasised — never a colour per company.
*/
function scatterChart(config) {
  const {
    points, xLabel, yLabel, highlight = null, height = 300,
    xFormat = Fmt.signedPct, yFormat = Fmt.signedPct,
    tableCaption = 'All plotted values',
  } = config;

  const W = 720;
  const H = height;
  const pad = { t: 16, r: 20, b: 42, l: 56 };
  const plotW = W - pad.l - pad.r;
  const plotH = H - pad.t - pad.b;
  const xs = niceScale(Math.min(...points.map((p) => p.x)), Math.max(...points.map((p) => p.x)), 6);
  const ys = niceScale(Math.min(...points.map((p) => p.y)), Math.max(...points.map((p) => p.y)), 5);
  const X = (v) => pad.l + ((v - xs.min) / (xs.max - xs.min)) * plotW;
  const Y = (v) => pad.t + plotH - ((v - ys.min) / (ys.max - ys.min)) * plotH;

  const container = h('div', { class: 'chart' });
  const svg = svgEl('svg', { viewBox: `0 0 ${W} ${H}`, role: 'img', 'aria-label': config.ariaLabel || tableCaption });

  const grid = svgEl('g', { class: 'chart__grid' });
  for (const t of ys.ticks) {
    grid.append(svgEl('line', { x1: pad.l, x2: pad.l + plotW, y1: Y(t), y2: Y(t) }));
    const lb = svgEl('text', { class: 'chart__tick', x: pad.l - 8, y: Y(t) + 3.5, 'text-anchor': 'end' });
    lb.textContent = yFormat(t, 0);
    grid.append(lb);
  }
  for (const t of xs.ticks) {
    const lb = svgEl('text', { class: 'chart__tick', x: X(t), y: pad.t + plotH + 17, 'text-anchor': 'middle' });
    lb.textContent = xFormat(t, 0);
    grid.append(lb);
  }
  svg.append(grid);

  for (const [v, horiz] of [[0, true], [0, false]]) {
    if (horiz && ys.min < 0 && ys.max > 0) {
      svg.append(svgEl('line', { x1: pad.l, x2: pad.l + plotW, y1: Y(0), y2: Y(0), stroke: cssVar('--axis'), 'stroke-width': 1 }));
    }
    if (!horiz && xs.min < 0 && xs.max > 0) {
      svg.append(svgEl('line', { x1: X(0), x2: X(0), y1: pad.t, y2: pad.t + plotH, stroke: cssVar('--axis'), 'stroke-width': 1 }));
    }
  }

  const axX = svgEl('text', { class: 'chart__tick', x: pad.l + plotW / 2, y: H - 6, 'text-anchor': 'middle' });
  axX.textContent = xLabel;
  svg.append(axX);
  const axY = svgEl('text', { class: 'chart__tick', x: 12, y: pad.t + plotH / 2, 'text-anchor': 'middle', transform: `rotate(-90 12 ${pad.t + plotH / 2})` });
  axY.textContent = yLabel;
  svg.append(axY);

  const tip = makeTooltip(container);
  const s1 = cssVar('--s1');
  const muted = cssVar('--ink-faint');

  for (const p of points) {
    const on = highlight === p.id;
    const dot = svgEl('circle', {
      cx: X(p.x), cy: Y(p.y), r: on ? 7 : 5,
      fill: on ? s1 : muted, 'fill-opacity': on ? 1 : 0.55,
      stroke: cssVar('--surface'), 'stroke-width': 2, class: 'chart__mark',
    });
    svg.append(dot);
    if (on) {
      const lb = svgEl('text', { class: 'chart__label', x: X(p.x) + 12, y: Y(p.y) + 4, 'font-weight': 600 });
      lb.textContent = p.label;
      svg.append(lb);
    }
    /* a 24px hit area — a 10px dot is a pinpoint nobody lands on */
    const hit = svgEl('circle', {
      cx: X(p.x), cy: Y(p.y), r: 14, fill: 'transparent', tabindex: 0, role: 'img',
      'aria-label': `${p.label}: ${xLabel} ${xFormat(p.x)}, ${yLabel} ${yFormat(p.y)}`,
    });
    const show = (e) => {
      const cr = container.getBoundingClientRect();
      const br = svg.getBoundingClientRect();
      const px = e && e.clientX ? e.clientX - cr.left : br.left - cr.left + (X(p.x) / W) * br.width;
      const py = e && e.clientY ? e.clientY - cr.top : br.top - cr.top + (Y(p.y) / H) * br.height;
      dot.setAttribute('r', on ? 8 : 6.5);
      tip.show(px, py, p.label, [
        { color: on ? s1 : muted, name: xLabel, value: xFormat(p.x) },
        { color: null, name: yLabel, value: yFormat(p.y) },
      ]);
    };
    const hide = () => { dot.setAttribute('r', on ? 7 : 5); tip.hide(); };
    hit.addEventListener('pointerenter', show);
    hit.addEventListener('pointermove', show);
    hit.addEventListener('pointerleave', hide);
    hit.addEventListener('focus', () => show());
    hit.addEventListener('blur', hide);
    svg.append(hit);
  }

  container.append(svg);

  const table = h('div', { class: 'tablewrap', hidden: true });
  const t = h('table', { class: 'data' });
  t.append(h('caption', { text: tableCaption }));
  t.append(h('thead', {}, [h('tr', {}, [
    h('th', { scope: 'col', text: 'Company' }),
    h('th', { scope: 'col', class: 'n', text: xLabel }),
    h('th', { scope: 'col', class: 'n', text: yLabel }),
  ])]));
  const tb = h('tbody');
  for (const p of points) {
    tb.append(h('tr', {}, [
      h('th', { scope: 'row', text: p.label }),
      h('td', { class: 'n', text: xFormat(p.x) }),
      h('td', { class: 'n', text: yFormat(p.y) }),
    ]));
  }
  t.append(tb);
  table.append(t);
  return h('div', {}, [container, buildFoot(null, table), table]);
}

/* ============================================================= sparkline == */
function sparkline(values, { width = 104, height = 26, color = null, ariaLabel = '' } = {}) {
  const c = color || cssVar('--s1');
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = max - min || 1;
  const x = (i) => (i / (values.length - 1)) * (width - 8) + 4;
  const y = (v) => height - 4 - ((v - min) / span) * (height - 8);
  const svg = svgEl('svg', {
    viewBox: `0 0 ${width} ${height}`, width, height, role: 'img', 'aria-label': ariaLabel,
    focusable: 'false',
  });
  const d = values.map((v, i) => `${i ? 'L' : 'M'}${x(i)} ${y(v)}`).join(' ');
  svg.append(svgEl('path', {
    d: `${d} L${x(values.length - 1)} ${height} L${x(0)} ${height} Z`,
    fill: c, 'fill-opacity': 0.1, stroke: 'none',
  }));
  svg.append(svgEl('path', { d, fill: 'none', stroke: c, 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }));
  svg.append(svgEl('circle', {
    cx: x(values.length - 1), cy: y(values[values.length - 1]), r: 2.6,
    fill: c, stroke: cssVar('--surface'), 'stroke-width': 2,
  }));
  return svg;
}

/* ================================================================= meter == */
function meter(label, value, max, { tone = 'accent', valueText = null } = {}) {
  const pct = max > 0 ? Math.max(0, Math.min(100, (value / max) * 100)) : 0;
  return h('div', { class: 'meter' }, [
    h('div', { class: 'meter__row' }, [
      h('span', { text: label }),
      h('strong', { class: 'num', text: valueText || `${pct.toFixed(0)}%` }),
    ]),
    h('div', {
      class: 'meter__track', role: 'meter', 'aria-valuenow': String(Math.round(pct)),
      'aria-valuemin': '0', 'aria-valuemax': '100', 'aria-label': label,
    }, [
      h('div', { class: `meter__fill${tone === 'accent' ? '' : ` meter__fill--${tone}`}`, style: `width:${pct}%` }),
    ]),
  ]);
}

/* ================================================== status pip and label == */
const STATUS_ICON = {
  good: 'M2 6.4 L4.6 9 L10 3',                       /* tick */
  warning: 'M6 1.4 L11 10.2 L1 10.2 Z',              /* triangle */
  serious: 'M6 1.4 L11 10.2 L1 10.2 Z',
  critical: 'M6 1 L11 6 L6 11 L1 6 Z',               /* diamond */
};

function statusMark(tone, label) {
  const svg = svgEl('svg', { class: 'status__icon', viewBox: '0 0 12 12', 'aria-hidden': 'true', focusable: 'false' });
  const filled = tone !== 'good';
  svg.append(svgEl('path', {
    d: STATUS_ICON[tone] || STATUS_ICON.good,
    fill: filled ? 'currentColor' : 'none',
    stroke: 'currentColor',
    'stroke-width': filled ? 1 : 2,
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round',
  }));
  const wrap = h('span', { class: `status status--${tone}` });
  wrap.append(svg, h('span', { text: label }));
  return wrap;
}
