// Carousel slides (1080×1350) as standalone HyperFrames pages, rendered to PNG as stills.
//
//   1 cover        the headline number in the brand's type
//   2 money map    the 4:5 map (segments moved to slide 3)
//   3 segments     revenue by segment, one color, values and growth labelled (or cost lines)
//   4 margins      gross and operating margin vs a year ago (net margin this quarter only:
//                  one-offs in last year's tax line can distort it)
//   5 one dollar   cents of each revenue dollar, our calculation (or key numbers after a loss)
//   6 sources      filing, how to read the figures, the disclaimer, the call to action

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

export const SLIDE = { width: 1080, height: 1350, margin: 72 };

function page({ theme, body, title, extraCss = "" }) {
  const { width: W, height: H } = SLIDE;
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=${W}, height=${H}" />
<title>${esc(title)}</title>
<script src="assets/gsap.min.js"></script>
<style>
  @font-face { font-family: "Inter"; src: url("assets/InterVariable.woff2") format("woff2"); font-weight: 100 900; font-style: normal; }
  html, body { margin: 0; background: ${theme.background}; }
  body { font-family: "Inter", sans-serif; color: ${theme.ink}; font-feature-settings: "tnum" 1, "kern" 1; }
  #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: ${theme.background}; }
  .slide { position: absolute; inset: 0; padding: ${SLIDE.margin}px; display: flex; flex-direction: column; box-sizing: border-box; }
  .kicker { font-size: 34px; color: ${theme.ink_muted}; font-weight: 500; }
  .company { font-size: 44px; font-weight: 700; letter-spacing: -0.02em; }
  .company .ticker { color: ${theme.ink_muted}; font-weight: 500; }
  h1 { font-size: 72px; line-height: 1.05; letter-spacing: -0.03em; margin: 28px 0 0; font-weight: 800; text-wrap: balance; }
  .foot { margin-top: auto; display: flex; justify-content: space-between; align-items: flex-end; gap: 24px; font-size: 26px; color: ${theme.ink_muted}; line-height: 1.4; }
  .foot .brand { color: ${theme.ink}; font-weight: 700; white-space: nowrap; }
  .foot .num { font-weight: 600; white-space: nowrap; }
  ${extraCss}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="${W}" data-height="${H}" data-duration="1">
  <section id="slide" class="clip slide" data-start="0" data-duration="1">
${body}
  </section>
</div>
<script>
  const tl = gsap.timeline({ paused: true });
  tl.to({}, { duration: 1 });
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
</script>
</body>
</html>`;
}

const header = (m) => `<div class="company">${esc(m.company.name)} <span class="ticker">(${esc(m.company.ticker)})</span></div><div class="kicker">${esc(m.period_display)}</div>`;
const foot = (m, n, total, source = true) =>
  `<div class="foot"><div>${source ? `${esc(m.source_line)}<br>` : ""}${esc(m.disclaimer)}.</div><div style="text-align:right"><div class="num">${n}/${total}</div><div class="brand">Earnings Maps</div></div></div>`;

export function coverSlide(m, theme, n, total) {
  const css = `
  .hook { margin-top: auto; }
  .hook .pre, .hook .post { font-size: 84px; font-weight: 700; letter-spacing: -0.025em; line-height: 1.05; }
  .hook .num { font-size: 220px; font-weight: 800; letter-spacing: -0.05em; line-height: 1; color: ${theme.revenue}; margin: 6px 0 6px -10px; }
  .hook .sub { font-size: 48px; color: ${theme.ink_muted}; margin-top: 30px; font-weight: 500; }`;
  const body = `${header(m)}
    <div class="hook"><div class="pre">${esc(m.hook.pre)}</div><div class="num">${esc(m.hook.number)}</div><div class="post">${esc(m.hook.post)}</div><div class="sub">${esc(m.hook.sub)}</div></div>
    ${foot(m, n, total, false)}`;
  return page({ theme, body, title: `${m.id} carousel ${n}`, extraCss: css });
}

function barRows(rows, theme, color, maxValue) {
  // rows: [{label, value, valueText, note}]; one color, direct labels (dataviz: nominal categories)
  const track = 936 - 0;
  return rows
    .map((r) => {
      const w = Math.max(6, Math.round((r.value / maxValue) * track));
      return `<div class="row"><div class="lbl"><span>${esc(r.label)}</span><span class="val">${esc(r.valueText)}${r.note ? `<span class="note">${esc(r.note)}</span>` : ""}</span></div><div class="bar" style="width:${w}px;background:${color}"></div></div>`;
    })
    .join("\n");
}
const barCss = (theme) => `
  .rows { margin-top: 56px; display: flex; flex-direction: column; gap: 30px; }
  .row { display: flex; flex-direction: column; gap: 12px; }
  .lbl { display: flex; justify-content: space-between; align-items: baseline; gap: 24px; font-size: 44px; font-weight: 500; }
  .lbl .val { font-weight: 700; white-space: nowrap; }
  .lbl .note { color: ${theme.ink_muted}; font-weight: 500; margin-left: 18px; }
  .bar { height: 40px; border-radius: 3px; }`;

export function segmentsSlide(m, theme, n, total) {
  const segs = m.carousel.segments;
  let title, rows, color;
  if (segs.length) {
    title = "Where the revenue came from";
    rows = segs.map((s) => ({ label: s.name, value: s.value, valueText: s.display, note: s.change ? `${s.change} y/y` : "" }));
    color = theme.revenue;
  } else {
    title = "Where the costs went";
    rows = m.nodes.filter((x) => x.kind === "cost").map((x) => ({ label: x.label, value: x.value, valueText: x.display, note: x.note || "" }));
    color = theme.cost;
  }
  const max = Math.max(...rows.map((r) => r.value));
  const body = `${header(m)}<h1>${esc(title)}</h1><div class="rows">${barRows(rows, theme, color, max)}</div>${foot(m, n, total)}`;
  return page({ theme, body, title: `${m.id} carousel ${n}`, extraCss: barCss(theme) });
}

export function marginsSlide(m, theme, n, total) {
  const all = m.carousel.margins;
  const compare = all.filter((x) => x.label !== "Net margin");
  const net = all.find((x) => x.label === "Net margin");
  const prior = theme.ink_muted;
  const rowsHtml = compare
    .map((x) => {
      const scale = 880 / Math.max(...compare.flatMap((y) => [Math.abs(y.current), Math.abs(y.prior)]), 0.01);
      const wc = Math.max(6, Math.round(Math.abs(x.current) * scale));
      const wp = Math.max(6, Math.round(Math.abs(x.prior) * scale));
      return `<div class="mrow"><div class="lbl"><span>${esc(x.label)}${x.our_calculation ? '<span class="note">our calculation</span>' : ""}</span></div>
        <div class="pair"><div class="bar" style="width:${wc}px;background:${theme.profit}"></div><span class="v">${esc(x.current_display)}</span></div>
        <div class="pair"><div class="bar" style="width:${wp}px;background:${prior};opacity:0.55"></div><span class="v muted">${esc(x.prior_display)}</span></div></div>`;
    })
    .join("\n");
  const css = `${barCss(theme)}
  .legend { display: flex; gap: 36px; margin-top: 36px; font-size: 34px; color: ${theme.ink_muted}; }
  .legend i { display: inline-block; width: 28px; height: 28px; border-radius: 3px; vertical-align: -4px; margin-right: 12px; }
  .mrows { margin-top: 44px; display: flex; flex-direction: column; gap: 44px; }
  .mrow { display: flex; flex-direction: column; gap: 12px; }
  .pair { display: flex; align-items: center; gap: 20px; }
  .pair .bar { height: 44px; }
  .pair .v { font-size: 44px; font-weight: 700; }
  .pair .v.muted { color: ${theme.ink_muted}; font-weight: 500; }
  .net { margin-top: 56px; font-size: 44px; } .net b { font-weight: 800; }`;
  const body = `${header(m)}<h1>How much of each sale is kept</h1>
    <div class="legend"><span><i style="background:${theme.profit}"></i>This quarter</span><span><i style="background:${prior};opacity:0.55"></i>Same quarter last year</span></div>
    <div class="mrows">${rowsHtml}</div>
    ${net ? `<div class="net">Net margin this quarter: <b>${esc(net.current_display)}</b></div>` : ""}
    ${foot(m, n, total)}`;
  return page({ theme, body, title: `${m.id} carousel ${n}`, extraCss: css });
}

export function dollarSlide(m, theme, n, total) {
  const parts = m.carousel.dollar;
  if (!parts.length) {
    // after a loss there are no cents to split; show the key numbers instead
    const keys = m.nodes.filter((x) => ["revenue", "cost", "loss", "profit"].includes(x.kind));
    const rows = keys.map((x) => `<div class="krow"><span>${esc(x.label)}</span><b style="color:${x.kind === "loss" ? theme.cost : theme.ink}">${esc(x.kind === "loss" ? "−" + x.display.replace("−", "") : x.display)}</b></div>`).join("");
    const css = `.krows { margin-top: 56px; display: flex; flex-direction: column; } .krow { display: flex; justify-content: space-between; font-size: 52px; padding: 26px 0; border-bottom: 2px solid ${theme.rule}; } .krow b { font-weight: 800; }`;
    return page({ theme, body: `${header(m)}<h1>The quarter in numbers</h1><div class="krows">${rows}</div>${foot(m, n, total)}`, title: `${m.id} carousel ${n}`, extraCss: css });
  }
  const color = (k) => (k === "profit" ? theme.profit : theme.cost);
  const segs = parts.map((p) => `<div class="seg" style="flex:${p.cents};background:${color(p.kind)}"></div>`).join("");
  const rows = parts.map((p) => `<div class="drow"><span><i style="background:${color(p.kind)}"></i>${esc(p.label)}</span><b>${p.cents}¢</b></div>`).join("");
  const css = `
  .stack { margin-top: 64px; display: flex; gap: 4px; height: 120px; } .seg { border-radius: 3px; min-width: 8px; }
  .drows { margin-top: 48px; display: flex; flex-direction: column; }
  .drow { display: flex; justify-content: space-between; align-items: center; font-size: 48px; padding: 22px 0; border-bottom: 2px solid ${theme.rule}; }
  .drow i { display: inline-block; width: 30px; height: 30px; border-radius: 3px; margin-right: 22px; vertical-align: -4px; }
  .drow b { font-weight: 800; }
  .calc { margin-top: 28px; font-size: 32px; color: ${theme.ink_muted}; }`;
  const body = `${header(m)}<h1>Every $1 of revenue, split</h1><div class="stack">${segs}</div><div class="drows">${rows}</div>
    <div class="calc">Our calculation from the release's figures, rounded to whole cents.</div>${foot(m, n, total)}`;
  return page({ theme, body, title: `${m.id} carousel ${n}`, extraCss: css });
}

export function sourcesSlide(m, theme, n, total) {
  const s = m.carousel.sources;
  const css = `
  .src { margin-top: 48px; display: flex; flex-direction: column; gap: 22px; font-size: 38px; line-height: 1.35; }
  .src .muted { color: ${theme.ink_muted}; }
  .src .url { font-size: 28px; color: ${theme.ink_muted}; word-break: break-all; }
  .cta { margin-top: 56px; font-size: 52px; font-weight: 800; letter-spacing: -0.02em; color: ${theme.accent}; line-height: 1.15; }
  .cta .sub { display: block; font-size: 40px; font-weight: 600; color: ${theme.ink}; margin-top: 14px; }`;
  const filed = new Date(s.filed + "T00:00:00Z").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
  const body = `${header(m)}<h1>Sources</h1>
    <div class="src">
      <div>${esc(m.company.name)} earnings release, ${esc(s.form)} ${esc(s.exhibit)}, filed ${esc(filed)}</div>
      <div class="url">${esc(s.url)}</div>
      <div class="muted">Figures as printed. "Our calculation" marks subtotals we computed. ${esc(m.basis_line)}.</div>
      <div><b>${esc(m.disclaimer)}.</b></div>
    </div>
    <div class="cta">Follow for more maps<span class="sub">Comment MAP for the full breakdown</span></div>
    ${foot(m, n, total, false)}`;
  return page({ theme, body, title: `${m.id} carousel ${n}`, extraCss: css });
}
