// Two more video formats from the same view model (1080×1920, beats follow the voiceover):
//
//   dollar-split  "Every $1 … split": one tall dollar bar fills with each cost's cents, then profit
//   kpi-cards     the quarter in four numbers: cards land one by one, values count up
//
// Same rules as the money map: one paused GSAP timeline, local fonts and GSAP, voice clips at the
// composition root, required lines on screen (company, period, source, basis, disclaimer).
// Text is measured with the layout's font metrics, so nothing is placed by guesswork.

import { textWidth } from "../../scripts/layout.mjs";

const W = 1080;
const H = 1920;
const MINUS = "−";
const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

// greedy word wrap at a measured width
function wrap(text, size, weight, width) {
  const lines = [];
  for (const word of String(text).split(/ +/)) { // regular spaces only, so a no-break space keeps words together
    const line = lines.length ? `${lines.at(-1)} ${word}` : word;
    if (lines.length && textWidth(line, size, weight) <= width) lines[lines.length - 1] = line;
    else lines.push(word);
  }
  return lines;
}

// same line count as wrap(), lines as even as possible (no lone last word)
function balance(text, size, weight, width) {
  const n = wrap(text, size, weight, width).length;
  let lo = width / n;
  let hi = width;
  while (hi - lo > 2) {
    const mid = (lo + hi) / 2;
    if (wrap(text, size, weight, mid).length > n) lo = mid;
    else hi = mid;
  }
  return wrap(text, size, weight, hi);
}

// shared frame: header, hook, footer, preview marker, voice clips, timeline scaffold
function frame(tokens, theme) {
  const safe = tokens.safe_zone_9x16;
  const x0 = safe.left_px;
  const x1 = W - safe.right_px;
  const footerTop = H - safe.bottom_px - 84;
  const hookTop = safe.top_px + 146;
  return { safe, x0, x1, footerTop, hookTop, hook: { size: 72, weight: theme.style.hero_weight, lead: 78 } };
}

function shell({ model, theme, tokens, beats, duration, preview, fr, hookLines, body, css, script }) {
  const audio = beats
    .filter((b) => b.src)
    .map((b) => `<audio id="vo-${b.src.match(/(\d+)\.wav$/)[1]}" src="${b.src}" data-start="${(b.start + 0.15).toFixed(2)}" data-duration="${b.audio.toFixed(2)}" data-volume="1"></audio>`)
    .join("\n  ");
  const BEATS = beats.map(({ beat, start, dur }) => ({ beat, start, dur }));
  return `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=${W}, height=${H}" />
<title>${esc(model.company.name)} ${esc(model.id)}</title>
<script src="assets/gsap.min.js"></script>
<style>
  @font-face { font-family: "Inter"; src: url("assets/InterVariable.woff2") format("woff2"); font-weight: 100 900; font-style: normal; }
  html, body { margin: 0; background: ${theme.background}; }
  body { font-family: "Inter", sans-serif; color: ${theme.ink}; font-feature-settings: "tnum" 1, "kern" 1; }
  #root { position: relative; width: 100%; height: 100%; overflow: hidden; background: ${theme.background}; }
  .layer { position: absolute; inset: 0; }
  #header { position: absolute; left: ${fr.x0}px; right: ${W - fr.x1}px; top: ${fr.safe.top_px}px; }
  #header .company { font-size: 56px; font-weight: ${theme.style.header_weight}; letter-spacing: -0.02em; line-height: 64px; }
  #header .ticker { color: ${theme.ink_muted}; font-weight: 500; }
  #header .period { font-size: 40px; color: ${theme.ink_muted}; line-height: 48px; margin-top: 2px; }
  #hook { position: absolute; left: ${fr.x0}px; top: ${fr.hookTop}px; font-size: ${fr.hook.size}px; font-weight: ${fr.hook.weight}; line-height: ${fr.hook.lead}px; letter-spacing: -0.02em; }
  #footer { position: absolute; left: ${fr.x0}px; right: ${W - fr.x1}px; top: ${fr.footerTop}px; font-size: 30px; line-height: 38px; color: ${theme.ink_muted}; }
  #footer .row2 { display: flex; justify-content: space-between; gap: 24px; }
  #footer .brand { color: ${theme.ink}; font-weight: 700; white-space: nowrap; }
  #preview { position: absolute; left: ${fr.x0}px; top: 96px; font-size: 26px; font-weight: 600; color: ${theme.accent}; }
  ${css}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-width="${W}" data-height="${H}" data-duration="${duration}">
  <section id="stage" class="clip layer" data-start="0" data-duration="${duration}">
    <div id="header">
      <div class="company">${esc(model.company.name)} <span class="ticker">(${esc(model.company.ticker)})</span></div>
      <div class="period">${esc(model.period_display)}</div>
    </div>
    <div id="hook">${hookLines.map(esc).join("<br>")}</div>
    ${body}
    <div id="footer">
      <div>${esc(model.source_line)}</div>
      <div class="row2"><span>${esc(model.basis_line)}. ${esc(model.disclaimer)}.</span><span class="brand">${esc(tokens.brand.name)}</span></div>
    </div>
    ${preview ? `<div id="preview">Style preview. Not approved for publishing.</div>` : ""}
  </section>
  ${audio}
</div>
<script>
(function () {
  const BEATS = ${JSON.stringify(BEATS)};
  const tl = gsap.timeline({ paused: true, defaults: { ease: "power2.out" } });
  gsap.set(["#header", "#footer"], { opacity: 0 });
  for (const b of BEATS.filter((x) => x.beat === "hook")) {
    tl.fromTo("#hook", { opacity: 0, y: 30 }, { opacity: 1, y: 0, duration: 0.5 }, b.start + 0.1);
    tl.to(["#header", "#footer"], { opacity: 1, duration: 0.4 }, b.start + 0.4);
  }
  ${script}
  tl.to({}, { duration: 0.01 }, ${duration} - 0.01);
  window.__timelines = window.__timelines || {};
  window.__timelines["main"] = tl;
})();
</script>
</body>
</html>
`;
}

// ---- dollar split -----------------------------------------------------------------------------

const DS = { barW: 400, gap: 48, cents: 88, label: 40, labelLead: 48, between: 22, sep: 3 };

export function dollarGeometry(model, tokens, theme) {
  const f = model.formats.dollar_split;
  const fr = frame(tokens, theme);
  const hookLines = balance(f.hook, fr.hook.size, fr.hook.weight, fr.x1 - fr.x0);
  const capTop = fr.hookTop + hookLines.length * fr.hook.lead + 40;
  const barTop = capTop + 52;
  const calcTop = fr.footerTop - 76;
  const barBottom = calcTop - 28;
  const barH = barBottom - barTop;
  const labelX = fr.x0 + DS.barW + DS.gap;
  const labelW = fr.x1 - labelX;
  let y = barTop;
  const parts = f.parts.map((p, i) => {
    const h = Math.round((p.cents / 100) * barH);
    const lines = wrap(p.label, DS.label, 500, labelW);
    const box = DS.cents + 6 + lines.length * DS.labelLead;
    const part = { ...p, i, y, h, lines, box, mid: y + h / 2 };
    y += h;
    return part;
  });
  parts.at(-1).h = barBottom - parts.at(-1).y; // whole cents can sum to the pixel; the last part takes the rounding
  parts.at(-1).mid = parts.at(-1).y + parts.at(-1).h / 2;
  // labels centre their cents figure on their part, then are pushed apart (down, then back up from the bottom)
  for (const [k, p] of parts.entries()) {
    p.ly = p.mid - DS.cents / 2;
    if (k) p.ly = Math.max(p.ly, parts[k - 1].ly + parts[k - 1].box + DS.between);
  }
  for (let k = parts.length - 1; k >= 0; k--) {
    const limit = k === parts.length - 1 ? barBottom - parts[k].box : parts[k + 1].ly - DS.between - parts[k].box;
    parts[k].ly = Math.round(Math.min(parts[k].ly, limit));
  }
  const warnings = [];
  if (parts[0].ly < capTop) warnings.push(`dollar-split labels start above the bar (${parts[0].ly} < ${capTop})`);
  for (const p of parts) if (p.h < 6) warnings.push(`dollar-split part "${p.label}" is under 6 px tall`);
  return { fr, hookLines, capTop, barTop, barBottom, barH, labelX, labelW, calcTop, parts, warnings };
}

export function dollarSplitHtml({ model, theme, tokens, beats, duration, preview = false }) {
  const g = dollarGeometry(model, tokens, theme);
  const { fr, parts } = g;
  const color = (p) => (p.kind === "profit" ? theme.profit : theme.cost);
  const leaders = parts
    .map((p) => {
      const ty = p.ly + DS.cents / 2;
      if (Math.abs(ty - p.mid) < 24) return "";
      const xa = fr.x0 + DS.barW + 8;
      const xb = g.labelX - 12;
      return `<path class="leader" data-i="${p.i}" d="M${xa} ${p.mid.toFixed(1)} L${xa + 10} ${p.mid.toFixed(1)} L${xb - 10} ${ty.toFixed(1)} L${xb} ${ty.toFixed(1)}" fill="none" stroke="${theme.ink_muted}" stroke-width="2"/>`;
    })
    .join("");
  const body = `
    <div id="cap">= $1 of revenue (100¢)</div>
    <div id="dollar"></div>
    ${parts
      .map((p) => {
        const top = p.y + (p.i ? DS.sep : 0);
        return `<div class="part" data-i="${p.i}" style="top:${top}px;height:${p.h - (p.i ? DS.sep : 0)}px;background:${color(p)}"></div>
    <div class="plabel" data-i="${p.i}" style="top:${p.ly}px"><div class="cents" data-cents="${p.cents}">${p.cents}¢</div><div class="what">${p.lines.map(esc).join("<br>")}</div></div>`;
      })
      .join("\n    ")}
    <svg id="leaders" class="layer" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${leaders}</svg>
    <div id="calc">Our calculation from the release, in whole cents.</div>`;
  const css = `
  #cap { position: absolute; left: ${fr.x0}px; top: ${g.capTop}px; font-size: 34px; line-height: 40px; color: ${theme.ink_muted}; }
  #dollar { position: absolute; left: ${fr.x0}px; top: ${g.barTop}px; width: ${DS.barW}px; height: ${g.barH}px; box-sizing: border-box; border: 3px solid ${theme.rule}; border-radius: ${theme.style.bar_radius + 2}px; }
  .part { position: absolute; left: ${fr.x0}px; width: ${DS.barW}px; border-radius: ${theme.style.bar_radius}px; }
  .plabel { position: absolute; left: ${g.labelX}px; width: ${g.labelW}px; }
  .plabel .cents { font-size: ${DS.cents}px; font-weight: ${theme.style.hero_weight}; letter-spacing: -0.03em; line-height: ${DS.cents}px; }
  .plabel .what { font-size: ${DS.label}px; line-height: ${DS.labelLead}px; color: ${theme.ink_muted}; font-weight: 500; margin-top: 6px; }
  #calc { position: absolute; left: ${fr.x0}px; right: ${W - fr.x1}px; top: ${g.calcTop}px; font-size: 32px; line-height: 40px; color: ${theme.ink_muted}; }`;
  const script = `
  const parts = Array.from(document.querySelectorAll(".part")), labels = Array.from(document.querySelectorAll(".plabel"));
  const leaders = (i) => Array.from(document.querySelectorAll('.leader[data-i="' + i + '"]'));
  gsap.set([parts, labels, Array.from(document.querySelectorAll(".leader")), "#dollar", "#cap", "#calc"], { opacity: 0 });
  let k = 0;
  for (const b of BEATS) {
    if (b.beat === "hook") {
      tl.to(["#dollar", "#cap"], { opacity: 1, duration: 0.4 }, b.start + 0.6);
    } else if (b.beat === "part" && k < parts.length) {
      const i = k, c = labels[i].querySelector(".cents"), target = +c.dataset.cents, box = { v: 0 };
      tl.fromTo(parts[i], { opacity: 0, scaleY: 0, transformOrigin: "50% 0%" }, { opacity: 1, scaleY: 1, duration: 0.6 }, b.start + 0.1);
      tl.fromTo(labels[i], { opacity: 0, x: 24 }, { opacity: 1, x: 0, duration: 0.4 }, b.start + 0.25);
      if (leaders(i).length) tl.to(leaders(i), { opacity: 1, duration: 0.3 }, b.start + 0.3);
      tl.to(box, { v: target, duration: 0.7, ease: "power1.out", onUpdate: function () { c.textContent = (this.progress() >= 1 ? target : Math.round(box.v)) + "\\u00a2"; } }, b.start + 0.25);
      k++;
    } else if (b.beat === "end") {
      tl.to("#calc", { opacity: 1, duration: 0.4 }, b.start + 0.1);
    }
  }`;
  return shell({ model, theme, tokens, beats, duration, preview, fr, hookLines: g.hookLines, body, css, script });
}

// ---- KPI cards --------------------------------------------------------------------------------

const KC = { gap: 26, pad: 30, label: 42, labelLead: 50, value: 108, sub: 36, subLead: 44, maxH: 230 };

export function kpiGeometry(model, tokens, theme) {
  const f = model.formats.kpi_cards;
  const fr = frame(tokens, theme);
  const hookLines = balance(f.hook, fr.hook.size, fr.hook.weight, fr.x1 - fr.x0);
  const top = fr.hookTop + hookLines.length * fr.hook.lead + 44;
  const bottom = fr.footerTop - 36;
  const n = f.cards.length;
  const cardH = Math.min(KC.maxH, Math.floor((bottom - top - (n - 1) * KC.gap) / n));
  const inner = fr.x1 - fr.x0 - 2 * KC.pad;
  const warnings = [];
  const cards = f.cards.map((c, i) => {
    const neg = c.value < 0;
    const shown = neg ? MINUS + c.display.replace(/^[-−]/, "") : c.display;
    const vw = textWidth(shown, KC.value, theme.style.hero_weight);
    const subW = Math.floor(inner - vw - 28);
    const subLines = balance(c.sub, KC.sub, 400, subW);
    if (subLines.length > 2 || subLines.some((s) => textWidth(s, KC.sub, 400) > subW)) warnings.push(`kpi card "${c.label}": sub line does not fit beside ${shown}`);
    return { ...c, i, neg, shown, top: top + i * (cardH + KC.gap), subW, subLines };
  });
  if (cardH < KC.pad * 2 + KC.labelLead + KC.value - 12) warnings.push(`kpi cards squeezed to ${cardH}px`);
  return { fr, hookLines, top, cardH, cards, warnings };
}

export function kpiCardsHtml({ model, theme, tokens, beats, duration, preview = false }) {
  const g = kpiGeometry(model, tokens, theme);
  const { fr } = g;
  const body = g.cards
    .map(
      (c) => `<div class="card" data-i="${c.i}" style="top:${c.top}px">
      <div class="lbl">${esc(c.label)}</div>
      <div class="val" data-value="${c.value}" data-display="${esc(c.shown)}" data-per-share="${c.per_share ? 1 : 0}"${c.neg ? ` style="color:${theme.cost}"` : ""}>${esc(c.shown)}</div>
      <div class="sub" style="max-width:${c.subW}px">${c.subLines.map(esc).join("<br>")}</div></div>`,
    )
    .join("\n    ");
  const css = `
  .card { position: absolute; left: ${fr.x0}px; width: ${fr.x1 - fr.x0}px; height: ${g.cardH}px; box-sizing: border-box; padding: ${KC.pad - 4}px ${KC.pad}px ${KC.pad - 6}px; background: ${theme.surface}; border-radius: ${theme.style.bar_radius + 8}px; box-shadow: 0 0 0 2px ${theme.rule}; display: grid; grid-template-columns: auto 1fr; grid-template-rows: auto 1fr; column-gap: 28px; }
  .card .lbl { font-size: ${KC.label}px; line-height: ${KC.labelLead}px; color: ${theme.ink_muted}; font-weight: 500; grid-column: 1 / 3; }
  .card .val { font-size: ${KC.value}px; font-weight: ${theme.style.hero_weight}; letter-spacing: -0.03em; line-height: ${KC.value}px; align-self: end; white-space: nowrap; }
  .card .sub { font-size: ${KC.sub}px; line-height: ${KC.subLead}px; color: ${theme.ink_muted}; align-self: end; justify-self: end; text-align: right; padding-bottom: 10px; }`;
  const script = `
  const MINUS = "\\u2212";
  function money(v, perShare) {
    const a = Math.abs(v), s = v < 0 ? MINUS : "";
    if (perShare) return s + "$" + a.toFixed(2);
    if (a >= 1e9) return s + "$" + (a / 1e9).toFixed(1) + "B";
    return s + "$" + Math.round(a / 1e6) + "M";
  }
  const cards = Array.from(document.querySelectorAll(".card"));
  gsap.set(cards, { opacity: 0 });
  let k = 0;
  for (const b of BEATS) {
    if (b.beat !== "card" || k >= cards.length) continue;
    const c = cards[k], v = c.querySelector(".val"), target = +v.dataset.value, ps = v.dataset.perShare === "1", box = { v: 0 };
    tl.fromTo(c, { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.5 }, b.start + 0.05);
    tl.to(box, { v: target, duration: 0.9, ease: "power1.out", onUpdate: function () { v.textContent = this.progress() >= 1 ? v.dataset.display : money(box.v, ps); } }, b.start + 0.15);
    k++;
  }`;
  return shell({ model, theme, tokens, beats, duration, preview, fr, hookLines: g.hookLines, body, css, script });
}
