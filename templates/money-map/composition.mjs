// Money map composition: model + baked layout + theme → one standalone HyperFrames HTML page.
//
// One paused GSAP timeline (window.__timelines.main), no clocks, no randomness, no network:
// GSAP and Inter are local files copied next to index.html. The story (about 30 s):
//   0–2 s    hook card
//   2–17 s   the map builds top to bottom, one row every ~3 s, numbers counting up
//   18–26 s  one insight: everything dims except the focus, a callout explains it
//   26–30 s  end card: the full map, the call to action, and a clean final frame for screenshots

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

function luminance(hex) {
  const v = hex.replace("#", "").match(/../g).map((h) => parseInt(h, 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
  return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2];
}
function contrast(a, b) {
  const [x, y] = [luminance(a), luminance(b)].sort((m, n) => n - m);
  return (x + 0.05) / (y + 0.05);
}
const onFill = (fill) => (contrast("#FFFFFF", fill) >= contrast("#0B0D10", fill) ? "#FFFFFF" : "#0B0D10");

export function buildHtml({ model, layout, theme, themeName, tokens, preview = false, duration = 30 }) {
  const st = theme.style;
  const W = layout.canvas.width;
  const H = layout.canvas.height;
  const f = layout.frame;
  const fill = { segment: theme.revenue, revenue: theme.revenue, cost: theme.cost, profit: theme.profit, other: theme.profit, loss: theme.cost };
  const flowFill = { revenue: theme.revenue, cost: theme.cost, profit: theme.profit, other: theme.profit, loss: theme.cost };
  const nodeById = Object.fromEntries(model.nodes.map((n) => [n.id, n]));
  const rows = layout.rows;

  // ---- timing ----------------------------------------------------------------------------
  const T0 = 2.5;
  const STEP = Math.min(3.0, 15.0 / Math.max(rows, 1));
  const rowAt = (r) => T0 + r * STEP;
  const insightStart = Math.max(rowAt(rows - 1) + 3.2, 17.5);
  const insightEnd = 25.6;
  const endStart = 26.0;

  // ---- svg: links, bars, labels, leaders -------------------------------------------------
  const linkEls = layout.links
    .map((l, i) => {
      const loss = l.kind === "loss";
      const paint = loss ? "url(#hatch)" : flowFill[l.kind] || theme.revenue;
      return `<path class="flow" id="flow-${i}" data-src="${esc(l.source)}" data-tgt="${esc(l.target)}" d="${l.d}" fill="${paint}" fill-opacity="${loss ? 0.9 : st.flow_opacity}" clip-path="url(#clip-row-${l.row})"/>`;
    })
    .join("\n      ");
  const clipEls = Array.from({ length: rows }, (_, r) => {
    const ls = layout.links.filter((l) => l.row === r);
    if (!ls.length) return "";
    const y = Math.min(...ls.map((l) => l.y));
    const h = Math.max(...ls.map((l) => l.y + l.h)) - y;
    return `<clipPath id="clip-row-${r}"><rect id="clip-rect-${r}" x="0" y="${y}" width="${W}" height="${h}" data-h="${h}"/></clipPath>`;
  }).join("\n      ");
  const barEls = layout.nodes
    .map((n) => {
      const paint = n.kind === "loss" ? "url(#hatch)" : fill[n.kind];
      return `<rect class="bar row-${n.row}" data-node="${esc(n.id)}" x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="${st.bar_radius}" fill="${paint}"/>`;
    })
    .join("\n      ");
  const color = { ink: theme.ink, "ink-muted": theme.ink_muted };
  const labelEls = layout.labels
    .map((t, i) => {
      const node = nodeById[t.node];
      const nodeRow = layout.nodes.find((n) => n.id === t.node)?.row ?? 0;
      const barFill = node && node.kind !== "loss" ? fill[node.kind] : theme.cost;
      const c = t.role === "on-fill" ? onFill(barFill) : color[t.role];
      const weight = t.hero ? st.hero_weight : t.weight >= 700 ? st.value_weight : t.weight;
      // count-up: labels whose text starts with the node's formatted value
      const disp = node ? (node.kind === "loss" ? "−" + node.display.replace("−", "") : node.display) : null;
      const counts = disp && t.text.startsWith(disp);
      const extra = counts ? ` data-count="${node.kind === "loss" ? -node.value : node.value}" data-suffix="${esc(t.text.slice(disp.length))}"` : "";
      return `<text class="label row-${nodeRow}${t.hero ? " hero" : ""}" id="label-${i}" data-node="${esc(t.node)}"${extra} x="${t.x}" y="${t.y}" font-size="${t.size}" font-weight="${weight}" text-anchor="${t.anchor}" fill="${c}">${esc(t.text)}</text>`;
    })
    .join("\n      ");
  const leaderEls = layout.leaders
    .map((l) => `<polyline class="leader row-0" data-node="${esc(l.node)}" points="${l.x1},${l.y1} ${l.x2},${l.y1} ${l.x2},${l.y2}" fill="none" stroke="${theme.ink_muted}" stroke-width="2" stroke-opacity="0.7"/>`)
    .join("\n      ");

  // ---- insight panel position: away from the focus row ------------------------------------
  const ins = model.insight;
  const focusNode = ins ? layout.nodes.find((n) => n.id === ins.node) : null;
  const panelTop = focusNode && focusNode.y < (f.firstRow + f.lastRow) / 2 ? f.lastRow - 90 : f.headerBottom + 20;
  const insightHtml = ins
    ? `<div id="insight" style="top:${panelTop}px"><div class="ins-head">${esc(ins.headline)}</div><div class="ins-sub">${esc(ins.sub)}</div></div>`
    : "";

  const company = model.company;
  const footerY = f.footerTop;

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=${W}, height=${H}" />
<title>${esc(company.name)} ${esc(model.id)} money map (${esc(themeName)})</title>
<script src="assets/gsap.min.js"></script>
<style>
  @font-face { font-family: "Inter"; src: url("assets/InterVariable.woff2") format("woff2"); font-weight: 100 900; font-style: normal; }
  html, body { margin: 0; background: ${theme.background}; }
  body { font-family: "Inter", sans-serif; color: ${theme.ink}; font-feature-settings: "tnum" 1, "kern" 1; }
  #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: ${theme.background}; }
  .layer { position: absolute; inset: 0; }
  svg text { font-family: "Inter", sans-serif; font-feature-settings: "tnum" 1; letter-spacing: -0.01em; }
  svg text.hero { letter-spacing: -0.035em; }
  #header { position: absolute; left: ${f.x0}px; right: ${W - f.x1}px; top: ${f.headerTop}px; }
  #header .company { font-size: 56px; font-weight: ${st.header_weight}; letter-spacing: -0.02em; line-height: 64px; }
  #header .ticker { color: ${theme.ink_muted}; font-weight: 500; }
  #header .period { font-size: 40px; color: ${theme.ink_muted}; line-height: 48px; margin-top: 2px; }
  #cta { position: absolute; right: ${W - f.x1}px; top: ${f.headerTop + (layout.header?.cta === "period" ? 72 : 18)}px; font-size: 32px;${layout.header?.cta === "none" ? " display: none;" : ""} font-weight: 700; color: ${theme.accent}; }
  #footer { position: absolute; left: ${f.x0}px; right: ${W - f.x1}px; top: ${footerY}px; font-size: 30px; line-height: 38px; color: ${theme.ink_muted}; }
  #footer .row2 { display: flex; justify-content: space-between; gap: 24px; }
  #footer .brand { color: ${theme.ink}; font-weight: 700; white-space: nowrap; }
  #preview { position: absolute; left: ${f.x0}px; top: 96px; font-size: 26px; font-weight: 600; color: ${theme.accent}; }
  #hook { position: absolute; left: ${f.x0}px; right: ${W - f.x1}px; top: 560px; }
  #hook .l1 { font-size: 80px; font-weight: ${st.header_weight}; line-height: 92px; letter-spacing: -0.02em; }
  #hook .num { font-size: 208px; font-weight: ${st.hero_weight}; line-height: 210px; letter-spacing: -0.045em; color: ${theme.revenue}; margin-left: -8px; }
  #hook .l2 { font-size: 52px; font-weight: 500; color: ${theme.ink_muted}; line-height: 64px; margin-top: 28px; }
  #insight { position: absolute; left: ${f.x0 - 24}px; right: ${W - f.x1 - 24}px; padding: 36px 40px; background: ${theme.surface}; border-radius: ${Math.max(st.bar_radius, 6)}px; box-shadow: 0 0 0 2px ${theme.rule}; }
  #insight .ins-head { font-size: 76px; font-weight: ${st.hero_weight}; line-height: 84px; letter-spacing: -0.025em; }
  #insight .ins-sub { font-size: 44px; font-weight: 500; color: ${theme.ink_muted}; line-height: 56px; margin-top: 10px; }
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="${W}" data-height="${H}" data-duration="${duration}">
  <section id="stage" class="clip layer" data-start="0" data-duration="${duration}">
    <svg id="map" class="layer" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" xmlns="http://www.w3.org/2000/svg">
      <defs>
        <pattern id="hatch" patternUnits="userSpaceOnUse" width="18" height="18" patternTransform="rotate(45)">
          <rect width="18" height="18" fill="${theme.cost}"/><rect width="7" height="18" fill="${theme.background}"/>
        </pattern>
      ${clipEls}
      </defs>
      <g id="flows">
      ${linkEls}
      </g>
      <g id="bars">
      ${barEls}
      </g>
      <g id="leaders">
      ${leaderEls}
      </g>
      <g id="labels">
      ${labelEls}
      </g>
    </svg>
    <div id="header">
      <div class="company">${esc(company.name)} <span class="ticker">(${esc(company.ticker)})</span></div>
      <div class="period">${esc(model.period_display)}</div>
    </div>
    <div id="cta">${esc(model.cta)}</div>
    <div id="footer">
      <div>${esc(model.source_line)}</div>
      <div class="row2"><span>${esc(model.basis_line)}. ${esc(model.disclaimer)}.</span><span class="brand">${esc(tokens.brand.name)}</span></div>
    </div>
    ${preview ? `<div id="preview">Style preview. Numbers audited, not yet approved for publishing.</div>` : ""}
    ${insightHtml}
    <div id="hook"><div class="l1">${esc(model.hook.pre)}</div><div class="num">${esc(model.hook.number)}</div><div class="l1">${esc(model.hook.post)}</div><div class="l2">${esc(model.hook.sub)}</div></div>
  </section>
</div>
<script>
(function () {
  const MINUS = "\\u2212";
  function money(v) {
    const a = Math.abs(v), s = v < 0 ? MINUS : "";
    if (a >= 1e9) return s + "$" + (Math.round(a / 1e8) / 10).toFixed(1) + "B";
    if (a >= 1e6) return s + "$" + Math.round(a / 1e6) + "M";
    return s + "$" + Math.round(a / 1e3) + "K";
  }
  const q = (sel) => Array.from(document.querySelectorAll(sel));
  const tl = gsap.timeline({ paused: true, defaults: { ease: "power2.out" } });

  // initial state
  gsap.set(["#header", "#footer", "#cta", ".bar", ".label", ".leader", "#insight"], { opacity: 0 });
  q("[id^=clip-rect-]").forEach((r) => r.setAttribute("height", 0));

  // hook
  tl.fromTo("#hook .l1", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, stagger: 0.25 }, 0.1)
    .fromTo("#hook .num", { opacity: 0, scale: 0.94, transformOrigin: "0% 50%" }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.4)" }, 0.3)
    .fromTo("#hook .l2", { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.4 }, 0.8)
    .to("#hook", { opacity: 0, y: -24, duration: 0.35, ease: "power2.in" }, ${(T0 - 0.55).toFixed(2)})
    .to(["#header", "#footer"], { opacity: 1, duration: 0.45 }, ${(T0 - 0.3).toFixed(2)});

  // rows, top to bottom
  const ROWS = ${rows};
  const rowAt = (r) => ${T0} + r * ${STEP};
  for (let r = 0; r < ROWS; r++) {
    const t = rowAt(r);
    if (r > 0) {
      const rect = document.getElementById("clip-rect-" + (r - 1));
      if (rect) tl.to(rect, { attr: { height: rect.dataset.h }, duration: 1.0, ease: "power1.inOut" }, t - 1.05);
    }
    tl.fromTo(".bar.row-" + r, { opacity: 0, scaleY: 0.2, transformOrigin: "50% 0%" }, { opacity: 1, scaleY: 1, duration: 0.45, stagger: 0.06 }, t);
    tl.to([".label.row-" + r, ".leader.row-" + r], { opacity: 1, duration: 0.35, stagger: 0.03 }, t + 0.2);
    q(".label.row-" + r + "[data-count]").forEach((el) => {
      const target = parseFloat(el.dataset.count), suffix = el.dataset.suffix || "";
      const box = { v: 0 };
      tl.to(box, { v: target, duration: 0.9, ease: "power1.out", onUpdate: () => { el.textContent = money(box.v) + suffix; } }, t + 0.2);
    });
  }
  tl.fromTo(".label.hero", { scale: 0.92, transformOrigin: "100% 100%" }, { scale: 1, duration: 0.6, ease: "back.out(1.6)" }, rowAt(ROWS - 1) + 0.25);

  // insight
  const focus = ${JSON.stringify(ins ? ins.node : null)};
  if (focus) {
    const dimmed = q(".bar, .label, .leader").filter((el) => el.dataset.node !== focus)
      .concat(q(".flow").filter((el) => el.dataset.src !== focus && el.dataset.tgt !== focus));
    tl.to(dimmed, { opacity: 0.16, duration: 0.5 }, ${insightStart.toFixed(2)});
    tl.fromTo("#insight", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.5 }, ${(insightStart + 0.35).toFixed(2)});
    tl.to("#insight", { opacity: 0, duration: 0.4 }, ${(insightEnd - 0.5).toFixed(2)});
    tl.to(q(".bar, .label, .leader"), { opacity: 1, duration: 0.5 }, ${insightEnd.toFixed(2)});
    tl.to(q(".flow"), { opacity: 1, duration: 0.5 }, ${insightEnd.toFixed(2)});
  }

  // end card
  tl.fromTo("#cta", { opacity: 0 }, { opacity: 1, duration: 0.5 }, ${endStart.toFixed(2)});
  tl.to({}, { duration: 0.01 }, ${duration - 0.01});
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
})();
</script>
</body>
</html>
`;
}
