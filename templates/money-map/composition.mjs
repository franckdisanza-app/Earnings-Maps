// Money map composition: model + baked layout + beat timings → one standalone HyperFrames page.
//
// One paused GSAP timeline (window.__timelines.main), no clocks, no randomness, no network:
// GSAP, Inter and the voice clips are local files next to index.html. The beats come from
// scripts/render.mjs and follow the voiceover:
//   hook        the headline number
//   row beats   each reveals its own nodes: incoming flows draw, bars land, numbers count up
//   insight     everything dims except the focus; a callout says what changed
//   end         the call to action; the full map holds as the screenshot frame

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

export function buildHtml({ model, layout, theme, themeName, tokens, preview = false, beats, duration }) {
  const st = theme.style;
  const W = layout.canvas.width;
  const H = layout.canvas.height;
  const f = layout.frame;
  const fill = { segment: theme.revenue, revenue: theme.revenue, cost: theme.cost, profit: theme.profit, other: theme.profit, loss: theme.cost };
  const flowFill = { revenue: theme.revenue, cost: theme.cost, profit: theme.profit, other: theme.profit, loss: theme.cost };
  const nodeById = Object.fromEntries(model.nodes.map((n) => [n.id, n]));

  // ---- svg: flows, bars, leaders, labels ---------------------------------------------------
  const linkEls = layout.links
    .map((l, i) => {
      const loss = l.kind === "loss";
      const paint = loss ? "url(#hatch)" : flowFill[l.kind] || theme.revenue;
      return `<path class="flow" id="flow-${i}" data-src="${esc(l.source)}" data-tgt="${esc(l.target)}" d="${l.d}" fill="${paint}" fill-opacity="${loss ? 0.9 : st.flow_opacity}"/>`;
    })
    .join("\n      ");
  const barEls = layout.nodes
    .map((n) => {
      const paint = n.kind === "loss" ? "url(#hatch)" : fill[n.kind];
      return `<rect class="bar" data-node="${esc(n.id)}" x="${n.x}" y="${n.y}" width="${n.w}" height="${n.h}" rx="${st.bar_radius}" fill="${paint}"/>`;
    })
    .join("\n      ");
  const color = { ink: theme.ink, "ink-muted": theme.ink_muted, loss: theme.cost };
  const labelEls = layout.labels
    .map((t, i) => {
      const node = nodeById[t.node];
      const barFill = node && node.kind !== "loss" ? fill[node.kind] : theme.cost;
      const c = t.role === "on-fill" ? onFill(barFill) : color[t.role];
      const weight = t.hero ? st.hero_weight : t.weight >= 700 ? st.value_weight : t.weight;
      const disp = node ? (node.kind === "loss" ? "−" + node.display.replace("−", "") : node.display) : null;
      const counts = disp && t.text.startsWith(disp);
      const extra = counts ? ` data-count="${node.kind === "loss" ? -node.value : node.value}" data-suffix="${esc(t.text.slice(disp.length))}"` : "";
      return `<text class="label${t.hero ? " hero" : ""}" id="label-${i}" data-node="${esc(t.node)}"${extra} x="${t.x}" y="${t.y}" font-size="${t.size}" font-weight="${weight}" text-anchor="${t.anchor}" fill="${c}">${esc(t.text)}</text>`;
    })
    .join("\n      ");
  const leaderEls = layout.leaders
    .map((l) => {
      const pts = l.x1 === l.x2 ? `${l.x1},${l.y1} ${l.x2},${l.y2}` : `${l.x1},${l.y1} ${l.x2},${l.y1} ${l.x2},${l.y2}`;
      return `<polyline class="leader" data-node="${esc(l.node)}" points="${pts}" fill="none" stroke="${theme.ink_muted}" stroke-width="2" stroke-opacity="0.7"/>`;
    })
    .join("\n      ");

  // ---- insight panel: away from the focus row --------------------------------------------
  const ins = model.insight;
  const focusNode = ins ? layout.nodes.find((n) => n.id === ins.node) : null;
  const panelTop = focusNode && focusNode.y < (f.firstRow + f.lastRow) / 2 ? f.lastRow - 90 : f.headerBottom + 20;
  const insightHtml = ins ? `<div id="insight" style="top:${panelTop}px"><div class="ins-head">${esc(ins.headline)}</div><div class="ins-sub">${esc(ins.sub)}</div></div>` : "";

  // ---- voice clips at the composition root (HyperFrames owns playback) --------------------
  const audioEls = beats
    .filter((b) => b.src)
    .map((b) => `<audio id="vo-${b.src.match(/(\d+)\.wav$/)[1]}" src="${b.src}" data-start="${(b.start + 0.15).toFixed(2)}" data-duration="${b.audio.toFixed(2)}" data-volume="1"></audio>`)
    .join("\n  ");

  const company = model.company;
  const ctaSlot = layout.header?.cta || "company";
  const BEATS = beats.map(({ beat, nodes, start, dur }) => ({ beat, nodes, start, dur }));

  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=${W}, height=${H}" />
<title>${esc(company.name)} ${esc(model.id)} money map</title>
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
  #cta { position: absolute; right: ${W - f.x1}px; top: ${f.headerTop + (ctaSlot === "period" ? 72 : 18)}px; font-size: 32px; font-weight: 700; color: ${theme.accent};${ctaSlot === "none" ? " display: none;" : ""} }
  #footer { position: absolute; left: ${f.x0}px; right: ${W - f.x1}px; top: ${f.footerTop}px; font-size: 30px; line-height: 38px; color: ${theme.ink_muted}; }
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
    ${preview ? `<div id="preview">Style preview. Not approved for publishing.</div>` : ""}
    ${insightHtml}
    <div id="hook"><div class="l1">${esc(model.hook.pre)}</div><div class="num">${esc(model.hook.number)}</div><div class="l1">${esc(model.hook.post)}</div><div class="l2">${esc(model.hook.sub)}</div></div>
  </section>
  ${audioEls}
</div>
<script>
(function () {
  const BEATS = ${JSON.stringify(BEATS)};
  const FOCUS = ${JSON.stringify(ins ? ins.node : null)};
  const MINUS = "\\u2212";
  function money(v) {
    const a = Math.abs(v), s = v < 0 ? MINUS : "";
    if (a >= 1e9) return s + "$" + (Math.round(a / 1e8) / 10).toFixed(1) + "B";
    if (a >= 1e6) return s + "$" + Math.round(a / 1e6) + "M";
    return s + "$" + Math.round(a / 1e3) + "K";
  }
  const q = (sel) => Array.from(document.querySelectorAll(sel));
  const ofNodes = (sel, ids, attr) => q(sel).filter((el) => ids.includes(el.dataset[attr || "node"]));
  const tl = gsap.timeline({ paused: true, defaults: { ease: "power2.out" } });

  gsap.set(["#header", "#footer", "#cta", ".bar", ".label", ".leader", ".flow", "#insight"], { opacity: 0 });

  // nodes no beat mentions are revealed with the first row beat
  const mentioned = new Set(BEATS.flatMap((b) => b.nodes));
  const firstRow = BEATS.find((b) => b.beat === "row");
  if (firstRow) q(".bar").forEach((el) => { if (!mentioned.has(el.dataset.node)) firstRow.nodes.push(el.dataset.node); });

  for (const b of BEATS) {
    const t = b.start, end = b.start + b.dur;
    if (b.beat === "hook") {
      tl.fromTo("#hook .l1", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.45, stagger: 0.25 }, t + 0.1)
        .fromTo("#hook .num", { opacity: 0, scale: 0.94, transformOrigin: "0% 50%" }, { opacity: 1, scale: 1, duration: 0.5, ease: "back.out(1.4)" }, t + 0.3)
        .fromTo("#hook .l2", { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.4 }, t + 0.8)
        .to("#hook", { opacity: 0, y: -24, duration: 0.35, ease: "power2.in" }, end - 0.45)
        .to(["#header", "#footer"], { opacity: 1, duration: 0.45 }, end - 0.3);
    } else if (b.beat === "row") {
      const flows = ofNodes(".flow", b.nodes, "tgt");
      const bars = ofNodes(".bar", b.nodes);
      const barAt = flows.length ? t + 0.6 : t + 0.1;
      if (flows.length) tl.fromTo(flows, { opacity: 0, scaleY: 0, transformOrigin: "50% 0%" }, { opacity: 1, scaleY: 1, duration: 0.8, ease: "power1.inOut" }, t);
      tl.fromTo(bars, { opacity: 0, scaleY: 0.2, transformOrigin: "50% 0%" }, { opacity: 1, scaleY: 1, duration: 0.45, stagger: 0.05 }, barAt);
      tl.to(ofNodes(".label", b.nodes).concat(ofNodes(".leader", b.nodes)), { opacity: 1, duration: 0.35, stagger: 0.02 }, barAt + 0.2);
      ofNodes(".label[data-count]", b.nodes).forEach((el) => {
        const target = parseFloat(el.dataset.count), suffix = el.dataset.suffix || "", box = { v: 0 };
        tl.to(box, { v: target, duration: 0.9, ease: "power1.out", onUpdate: () => { el.textContent = money(box.v) + suffix; } }, barAt + 0.2);
      });
      const hero = ofNodes(".label.hero", b.nodes);
      if (hero.length) tl.fromTo(hero, { scale: 0.92, transformOrigin: "100% 100%" }, { scale: 1, duration: 0.6, ease: "back.out(1.6)" }, barAt + 0.25);
    } else if (b.beat === "insight" && FOCUS) {
      const dimmed = q(".bar, .label, .leader").filter((el) => el.dataset.node !== FOCUS)
        .concat(q(".flow").filter((el) => el.dataset.src !== FOCUS && el.dataset.tgt !== FOCUS));
      tl.to(dimmed, { opacity: 0.16, duration: 0.5 }, t);
      tl.fromTo("#insight", { opacity: 0, y: 24 }, { opacity: 1, y: 0, duration: 0.5 }, t + 0.3);
      tl.to("#insight", { opacity: 0, duration: 0.4 }, end - 0.6);
      tl.to(q(".bar, .label, .leader, .flow"), { opacity: 1, duration: 0.45 }, end - 0.45);
    } else if (b.beat === "end") {
      tl.fromTo("#cta", { opacity: 0 }, { opacity: 1, duration: 0.5 }, t + 0.2);
    }
  }
  tl.to({}, { duration: 0.01 }, ${duration} - 0.01);
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
})();
</script>
</body>
</html>
`;
}
