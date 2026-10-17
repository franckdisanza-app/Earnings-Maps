// Compute the money map's geometry at build time and bake it into out/<ID>/build/layout.json.
//
//   node scripts/layout.mjs <ID>
//
// d3-sankey lays the flows out horizontally; we turn its depth axis into the vertical axis so the
// map reads top to bottom like an income statement (segments → revenue → gross profit →
// operating income → net income). Costs stay directly under the flow that feeds them, so flows
// run straight down and the space a finished cost leaves on the left becomes a label column.
// Revenue and profit bars grow tall enough to hold their own label (one line, two lines, or a
// wrapped name); cost labels go inside, else to the bar's left. Labels never sit on bars or
// flows. Nothing is random and nothing is measured at render time.

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
import { sankey, sankeyLeft } from "d3-sankey";

const require = createRequire(import.meta.url);
const fontkit = require("fontkit");
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

const tokens = JSON.parse(fs.readFileSync(path.join(ROOT, "brand/tokens.json"), "utf8"));
const font = fontkit.openSync(path.join(ROOT, "brand/fonts/InterVariable.ttf"));
const fontAt = new Map();

export function textWidth(text, size, weight = 400) {
  if (!fontAt.has(weight)) fontAt.set(weight, font.getVariation({ wght: weight, opsz: 32 }));
  const run = fontAt.get(weight).layout(String(text), ["tnum", "kern"]);
  return (run.advanceWidth / font.unitsPerEm) * size;
}

// ---- canvas -------------------------------------------------------------------------------
// default canvas: the 9:16 video; layout(model, { width, height, safe, segments }) for other formats
const VIDEO = { width: tokens.canvas.video.width, height: tokens.canvas.video.height, safe: tokens.safe_zone_9x16 };
export const METRICS = { T: 64, PAD: 20, GAP: 16, LABEL: 44, LINE: 52, NOTE: 34, HERO: 112, MIN_FLOW: 56, MAX_FLOW: 220 };
const { T, PAD, GAP, LABEL, LINE, NOTE, HERO, MIN_FLOW, MAX_FLOW } = METRICS;
const CAP = Math.round(LABEL * 0.75);
// Measure at the heaviest weights any theme draws (bold: values 800, hero 900) so every theme fits.
const VW = Math.max(...Object.values(tokens.themes).map((t) => t.style?.value_weight || 700));
const HW = Math.max(...Object.values(tokens.themes).map((t) => t.style?.hero_weight || 800));

const KIND_RANK = { cost: 0, segment: 1, revenue: 2, profit: 2, other: 3, loss: 3 };

function withoutSegments(m) {
  const segIds = new Set(m.nodes.filter((n) => n.kind === "segment").map((n) => n.id));
  return { ...m, nodes: m.nodes.filter((n) => !segIds.has(n.id)), links: m.links.filter((l) => !segIds.has(l.source)) };
}

function wrapName(name) {
  const words = name.split(" ");
  if (words.length < 2) return [name];
  let best = [name];
  let bestW = Infinity;
  for (let i = 1; i < words.length; i++) {
    const a = words.slice(0, i).join(" ");
    const b = words.slice(i).join(" ");
    if (/^(&|and|of|the)$/i.test(words[i])) continue; // don't start a line with a joining word
    const w = Math.max(textWidth(a, LABEL, 500), textWidth(b, LABEL, 500));
    if (w < bestW) {
      bestW = w;
      best = [a, b];
    }
  }
  return best;
}

export function layout(modelIn, opts = {}) {
  const W = opts.width ?? VIDEO.width;
  const H = opts.height ?? VIDEO.height;
  const SAFE = opts.safe ?? VIDEO.safe;
  const X0 = SAFE.left_px;
  const X1 = W - SAFE.right_px;
  const SPAN = X1 - X0;
  // the 4:5 carousel map leaves the segment row to its own slide
  const model = opts.segments === false ? withoutSegments(modelIn) : modelIn;
  const out = { canvas: { width: W, height: H }, nodes: [], links: [], labels: [], leaders: [], warnings: [] };
  const hasSegments = model.nodes.some((n) => n.kind === "segment");
  const headerBottom = SAFE.top_px + 108;
  const segLabelSpace = hasSegments ? 222 : 0;
  const top = headerBottom + (opts.headerGap ?? 12) + segLabelSpace;
  const footerTop = H - SAFE.bottom_px - 84;
  const heroBlock = LABEL + HERO + 56; // net income name, value, share line under its bar
  const HERO_DROP = CAP + 20 + HERO * 0.8; // name baseline to value baseline leaves room for descenders (p, g)

  const nodes = model.nodes.map((n, i) => ({ ...n, order: i }));
  const links = model.links.map((l) => ({ ...l }));
  const align = (node, n) => {
    if ((node.kind === "loss" || node.kind === "other") && node.sourceLinks.length) {
      return Math.max(0, node.sourceLinks[0].target.depth - 1);
    }
    return sankeyLeft(node, n);
  };
  const graph = { nodes, links };
  sankey()
    .nodeId((d) => d.id)
    .nodeAlign(align)
    .nodeWidth(T)
    .nodePadding(GAP)
    .nodeSort((a, b) => KIND_RANK[a.kind] - KIND_RANK[b.kind] || a.order - b.order)
    .linkSort(null)
    .iterations(32)
    .extent([[0, 0], [1000, SPAN]])(graph);
  const rows = Math.max(...graph.nodes.map((n) => n.layer)) + 1;
  out.rows = rows;

  // The payoff number: net income, or the loss when the story stops at a loss.
  const heroNode = graph.nodes.find((n) => n.id === "net_income" && n.kind === "profit") || graph.nodes.find((n) => n.kind === "loss");

  // Horizontal geometry from d3-sankey (its "y" axis is our x axis).
  for (const n of graph.nodes) n.rect = { x: X0 + n.y0, w: n.y1 - n.y0, h: T };

  // ---- 1) inside labels decide bar heights -------------------------------------------------
  const valueText = (n) => (n.kind === "loss" ? `−${n.display.replace("−", "")}` : n.display);
  const inside = new Map(); // node id -> { mode, lines }
  for (const n of graph.nodes.filter((m) => m.kind !== "segment" && m.kind !== "loss")) {
    if (n === heroNode) continue;
    const value = valueText(n);
    const extra = n.kind === "revenue" && n.change ? n.change : null;
    const valueLine = extra ? `${value}  ${extra}` : value;
    const room = n.rect.w - 2 * PAD;
    const nameW = textWidth(n.label, LABEL, 500);
    const valW = textWidth(valueLine, LABEL, VW);
    const wrapped = wrapName(n.label);
    const wrapW = Math.max(...wrapped.map((s) => textWidth(s, LABEL, 500)));
    if (nameW + 28 + valW <= room) {
      inside.set(n.id, { mode: "one", lines: [[n.label, 500], [valueLine, 700]] });
    } else if (Math.max(nameW, valW) <= room) {
      inside.set(n.id, { mode: "stack", lines: [[n.label, 500], [valueLine, 700]] });
      n.rect.h = 24 + 2 * LINE;
    } else if (wrapped.length > 1 && Math.max(wrapW, valW) <= room) {
      inside.set(n.id, { mode: "stack", lines: [[wrapped[0], 500], [wrapped[1], 500], [valueLine, 700]] });
      n.rect.h = 24 + 3 * LINE;
    }
  }

  // ---- 2) vertical geometry: rows stacked with equal flow length -------------------------
  const rowH = Array.from({ length: rows }, (_, r) => Math.max(...graph.nodes.filter((n) => n.layer === r).map((n) => n.rect.h)));
  const lastRowHasHero = Boolean(heroNode);
  const bottom = footerTop - 20 - (lastRowHasHero ? heroBlock : 0);
  let flow = rows > 1 ? (bottom - top - rowH.reduce((a, b) => a + b, 0)) / (rows - 1) : 0;
  if (flow < MIN_FLOW) out.warnings.push(`flows are only ${Math.round(flow)} px long`);
  // Few rows: cap the flow length and split the spare height above and below the map.
  let shift = 0;
  if (flow > MAX_FLOW) {
    shift = ((flow - MAX_FLOW) * (rows - 1)) / 2;
    flow = MAX_FLOW;
  }
  const rowY = [];
  let y = top + shift;
  for (let r = 0; r < rows; r++) {
    rowY.push(y);
    y += rowH[r] + flow;
  }
  for (const n of graph.nodes) n.rect.y = rowY[n.layer];

  // ---- 3) obstacles: bars and flows ------------------------------------------------------
  const placed = [];
  const pad = (b, p) => ({ x0: b.x0 - p, x1: b.x1 + p, y0: b.y0 - p, y1: b.y1 + p });
  const padX = (b, p) => ({ ...b, x0: b.x0 - p, x1: b.x1 + p });
  const hit = (b) => placed.some((p) => b.x0 < p.x1 && b.x1 > p.x0 && b.y0 < p.y1 && b.y1 > p.y0);
  const inBounds = (b) => b.x0 >= X0 - 0.5 && b.x1 <= X1 + 0.5 && b.y0 >= headerBottom + 8 && b.y1 <= footerTop - 8;
  for (const n of graph.nodes) placed.push(pad({ x0: n.rect.x, x1: n.rect.x + n.rect.w, y0: n.rect.y, y1: n.rect.y + n.rect.h }, 6));
  const r1 = (v) => Math.round(v * 10) / 10;
  for (const l of graph.links) {
    const xs = X0 + l.y0;
    const xt = X0 + l.y1;
    const ys = l.source.rect.y + l.source.rect.h;
    const yt = l.target.rect.y;
    l.geo = { xs, xt, ys, yt, w: l.width };
    // sample the band as boxes so a diagonal flow blocks only what it covers
    const ease = (t) => t * t * (3 - 2 * t);
    for (let k = 0; k < 6; k++) {
      const t0 = k / 6;
      const t1 = (k + 1) / 6;
      const xa = xs + (xt - xs) * ease(t0);
      const xb = xs + (xt - xs) * ease(t1);
      placed.push(pad({ x0: Math.min(xa, xb) - l.width / 2, x1: Math.max(xa, xb) + l.width / 2, y0: ys + (yt - ys) * t0, y1: ys + (yt - ys) * t1 }, 4));
    }
  }

  // ---- 4) emit labels -------------------------------------------------------------------
  const lab = (node, text, x, yy, size, weight, anchor, role, extra = {}) =>
    out.labels.push({ node: node.id, text, x: Math.round(x), y: Math.round(yy), size, weight, anchor, role, ...extra });

  for (const n of graph.nodes) {
    const spec = inside.get(n.id);
    if (!spec) continue;
    if (spec.mode === "one") {
      const cy = n.rect.y + n.rect.h / 2 + LABEL * 0.36;
      lab(n, spec.lines[0][0], n.rect.x + PAD, cy, LABEL, 500, "start", "on-fill");
      lab(n, spec.lines[1][0], n.rect.x + n.rect.w - PAD, cy, LABEL, 700, "end", "on-fill");
    } else {
      let yy = n.rect.y + 12 + CAP + 4;
      for (const [t, wt] of spec.lines) {
        lab(n, t, n.rect.x + PAD, yy, LABEL, wt, "start", "on-fill");
        yy += LINE;
      }
    }
    if (n.note) {
      const b = { x0: n.rect.x, x1: n.rect.x + textWidth(n.note, NOTE, 500), y0: n.rect.y + n.rect.h + 6, y1: n.rect.y + n.rect.h + 6 + NOTE };
      lab(n, n.note, n.rect.x + 2, b.y1 - 6, NOTE, 500, "start", "ink-muted");
      placed.push(b);
    }
  }

  // Net income: the payoff, under its bar, right-aligned, in the largest type.
  for (const n of heroNode ? [heroNode] : []) {
    const value = valueText(n);
    const inLastRow = n.layer === rows - 1;
    const xr = inLastRow ? n.rect.x + n.rect.w : X1;
    const yTop = Math.max(...graph.nodes.filter((m) => m.layer === rows - 1).map((m) => m.rect.y + m.rect.h)) + 14;
    lab(n, n.label, xr, yTop + CAP + 4, LABEL, 600, "end", "ink-muted");
    lab(n, value, xr, yTop + HERO_DROP, HERO, 800, "end", n.kind === "loss" ? "loss" : "ink", { hero: true });
    if (n.share) lab(n, n.share, xr, yTop + HERO_DROP + 46, NOTE + 4, 500, "end", "ink-muted");
    const w = Math.max(textWidth(value, HERO, HW), textWidth(n.label, LABEL, 600), n.share ? textWidth(n.share, NOTE + 4, 500) : 0);
    placed.push({ x0: xr - w - 16, x1: xr, y0: yTop - 4, y1: yTop + heroBlock });
  }

  // Everything else outside its bar: left of the bar (centred, then top- or bottom-aligned),
  // then right of it, then below; the widest form that fits, else the name wrapped.
  const forms = (n) => {
    const value = valueText(n);
    const list = [{ lines: [[n.label, 500, "ink-muted"], [value, 700, "ink"]] }];
    const wrapped = wrapName(n.label);
    if (wrapped.length > 1) list.push({ lines: [[wrapped[0], 500, "ink-muted"], [wrapped[1], 500, "ink-muted"], [value, 700, "ink"]] });
    for (const f of list) {
      if (n.note) f.lines.push([n.note, 500, "ink-muted", NOTE]);
      f.w = Math.max(...f.lines.map(([t, wt, , sz]) => textWidth(t, sz || LABEL, wt)));
      f.h = f.lines.reduce((h, [, , , sz]) => h + (sz ? NOTE + 10 : LINE), 0);
    }
    return list;
  };
  const emit = (n, f, x, yTop, anchor) => {
    let yy = yTop + CAP + 4;
    for (const [t, wt, role, sz] of f.lines) {
      lab(n, t, x, yy, sz || LABEL, wt, anchor, role);
      yy += sz ? NOTE + 10 : LINE;
    }
  };
  const rest = graph.nodes.filter((n) => n.kind !== "segment" && !inside.has(n.id) && n !== heroNode);
  rest.sort((a, b) => a.layer - b.layer);
  for (const n of rest) {
    let done = false;
    for (const f of forms(n)) {
      const yCands = [n.rect.y + n.rect.h / 2 - f.h / 2, n.rect.y - 4, n.rect.y + n.rect.h - f.h + 4];
      for (let k = 1; k <= 8; k++) yCands.push(n.rect.y - 4 + k * 13); // slide down, still touching the bar
      for (let k = 1; k <= 4; k++) yCands.push(n.rect.y + n.rect.h - f.h + 4 - k * 13);
      const tries = [];
      for (const y0 of yCands) tries.push({ x: n.rect.x - 18, anchor: "end", box: { x0: n.rect.x - 18 - f.w, x1: n.rect.x - 18, y0, y1: y0 + f.h } });
      for (const y0 of yCands) tries.push({ x: n.rect.x + n.rect.w + 18, anchor: "start", box: { x0: n.rect.x + n.rect.w + 18, x1: n.rect.x + n.rect.w + 18 + f.w, y0, y1: y0 + f.h } });
      tries.push({ x: n.rect.x, anchor: "start", box: { x0: n.rect.x, x1: n.rect.x + f.w, y0: n.rect.y + n.rect.h + 12, y1: n.rect.y + n.rect.h + 12 + f.h } });
      for (const t of tries) {
        if (inBounds(t.box) && !hit(t.box)) {
          emit(n, f, t.x, t.box.y0, t.anchor);
          placed.push(pad(t.box, 10));
          done = true;
          break;
        }
      }
      if (done) break;
    }
    if (!done) {
      const f = forms(n).at(-1);
      emit(n, f, n.rect.x - 18, n.rect.y, "end");
      out.warnings.push(`no free spot for the ${n.id} label; it overlaps`);
    }
  }

  // ---- 5) segment row: labels above the bars ----------------------------------------------
  const segs = graph.nodes.filter((n) => n.kind === "segment").sort((a, b) => a.rect.x - b.rect.x);
  const segBase = rowY[0] - 18;
  const tierTop = headerBottom + 20;
  const small = [];
  segs.forEach((n, i) => {
    const value = `${n.display}${n.change ? "  " + n.change : ""}`;
    const first = i === 0;
    const last = i === segs.length - 1 && segs.length > 1;
    const slack = first || last ? 90 : 30;
    const x = last ? n.rect.x + n.rect.w : n.rect.x;
    const one = textWidth(n.label, LABEL, 500) + 20 + textWidth(value, LABEL, VW);
    const two = Math.max(textWidth(n.label, LABEL, 500), textWidth(value, LABEL, VW));
    const boxFor = (w, lines) => {
      const y0 = segBase - (lines - 1) * LINE - CAP - 6;
      return last ? { x0: x - w, x1: x, y0, y1: segBase + 4 } : { x0: x, x1: x + w, y0, y1: segBase + 4 };
    };
    if (one <= n.rect.w + slack && !hit(padX(boxFor(one, 1), 10))) {
      if (last) {
        lab(n, value, x, segBase, LABEL, 700, "end", "ink");
        lab(n, n.label, x - textWidth(value, LABEL, VW) - 20, segBase, LABEL, 500, "end", "ink-muted");
      } else {
        lab(n, n.label, x, segBase, LABEL, 500, "start", "ink-muted");
        lab(n, value, x + textWidth(n.label, LABEL, 500) + 20, segBase, LABEL, 700, "start", "ink");
      }
      placed.push(padX(boxFor(one, 1), 18));
    } else if (two <= n.rect.w + slack && !hit(padX(boxFor(two, 2), 10))) {
      lab(n, n.label, x, segBase - LINE, LABEL, 500, last ? "end" : "start", "ink-muted");
      lab(n, value, x, segBase, LABEL, 700, last ? "end" : "start", "ink");
      placed.push(padX(boxFor(two, 2), 18));
    } else if (wrapName(n.label).length > 1 && Math.max(...wrapName(n.label).map((s) => textWidth(s, LABEL, 500)), textWidth(value, LABEL, VW)) <= n.rect.w + slack
               && segBase - 2 * LINE - CAP - 6 >= tierTop && !hit(padX(boxFor(Math.max(...wrapName(n.label).map((s) => textWidth(s, LABEL, 500)), textWidth(value, LABEL, VW)), 3), 10))) {
      const [a, b] = wrapName(n.label);
      const w3 = Math.max(textWidth(a, LABEL, 500), textWidth(b, LABEL, 500), textWidth(value, LABEL, VW));
      lab(n, a, x, segBase - 2 * LINE, LABEL, 500, last ? "end" : "start", "ink-muted");
      lab(n, b, x, segBase - LINE, LABEL, 500, last ? "end" : "start", "ink-muted");
      lab(n, value, x, segBase, LABEL, 700, last ? "end" : "start", "ink");
      placed.push(padX(boxFor(w3, 3), 18));
    } else {
      small.push(n);
    }
  });
  if (small.length) {
    // One line per small segment, stacked upward; the top line belongs to the rightmost bar so
    // leader lines nest without crossing, and the stack stays left of the bars it points to.
    const ordered = [...small].sort((a, b) => b.rect.x - a.rect.x);
    const lines = ordered.map((n) => [n.label, n.display]);
    const lineW = lines.map(([a, b]) => textWidth(a, LABEL, 500) + 16 + textWidth(b, LABEL, VW));
    const wMax = Math.max(...lineW);
    const step = LINE;
    const target = Math.min(...small.map((n) => n.rect.x + n.rect.w / 2)) - 28;
    if (wMax > SPAN) out.warnings.push("small segment labels are wider than the frame; give the segments short names");
    const xs = [target - wMax, X0, ...placed.map((p) => p.x1 + 2)]
      .map((v) => Math.max(X0, Math.min(v, X1 - wMax)))
      .sort((a, b) => Math.abs(a + wMax - target) - Math.abs(b + wMax - target));
    let spot = null;
    for (let lowest = 0; !spot; lowest++) {
      const yBottom = segBase - lowest * step;
      const yTopLine = yBottom - (small.length - 1) * step;
      if (yTopLine - CAP - 6 < tierTop) break;
      for (const sx of xs) {
        const box = { x0: sx, x1: sx + wMax, y0: yTopLine - CAP - 6, y1: yBottom + 4 };
        if (!hit(padX(box, 10))) {
          spot = { sx, yBottom };
          break;
        }
      }
    }
    if (!spot) {
      out.warnings.push("no free slot for the small segment labels");
      spot = { sx: X0, yBottom: segBase };
    }
    ordered.forEach((n, k) => {
      const yy = spot.yBottom - (small.length - 1 - k) * step;
      const [name, value] = lines[k];
      lab(n, name, spot.sx, yy, LABEL, 500, "start", "ink-muted", { stacked: true });
      lab(n, value, spot.sx + textWidth(name, LABEL, 500) + 16, yy, LABEL, 700, "start", "ink", { stacked: true });
      // drop the leader onto the bar where its vertical run misses every label
      const yLine = yy - CAP / 2;
      // label boxes carry 18 px of padding; a leader needs only ~8 px of clearance
      const clear = (x) => !placed.some((p) => x > p.x0 + 10 && x < p.x1 - 10 && p.y1 > yLine && p.y0 < n.rect.y - 6);
      const cx0 = n.rect.x + n.rect.w / 2;
      let cx = cx0;
      for (let dx = 0; dx <= n.rect.w / 2 - 4; dx += 2) {
        if (clear(cx0 - dx)) {
          cx = cx0 - dx;
          break;
        }
        if (clear(cx0 + dx)) {
          cx = cx0 + dx;
          break;
        }
      }
      const xEnd = spot.sx + lineW[k];
      if (cx <= xEnd + 6) {
        out.leaders.push({ node: n.id, x1: Math.round(cx), y1: Math.round(yy + 12), x2: Math.round(cx), y2: Math.round(n.rect.y - 6) });
      } else {
        out.leaders.push({ node: n.id, x1: Math.round(xEnd + 12), y1: Math.round(yLine), x2: Math.round(cx), y2: Math.round(n.rect.y - 6) });
      }
    });
    placed.push({ x0: spot.sx, x1: spot.sx + wMax, y0: spot.yBottom - small.length * step, y1: spot.yBottom + 10 });
  }

  // ---- 6) flows and nodes out ---------------------------------------------------------------
  for (const l of graph.links) {
    const { xs, xt, ys, yt, w } = l.geo;
    const ym = (ys + yt) / 2;
    const d = `M${r1(xs - w / 2)},${r1(ys)} C${r1(xs - w / 2)},${r1(ym)} ${r1(xt - w / 2)},${r1(ym)} ${r1(xt - w / 2)},${r1(yt)} L${r1(xt + w / 2)},${r1(yt)} C${r1(xt + w / 2)},${r1(ym)} ${r1(xs + w / 2)},${r1(ym)} ${r1(xs + w / 2)},${r1(ys)} Z`;
    out.links.push({ source: l.source.id, target: l.target.id, kind: l.kind, value: l.value, d, row: l.source.layer, x: r1(Math.min(xs, xt) - w / 2), y: r1(ys), w: r1(Math.abs(xt - xs) + w), h: r1(yt - ys) });
  }
  for (const n of graph.nodes) {
    out.nodes.push({ id: n.id, kind: n.kind, label: n.label, display: n.display, row: n.layer, x: r1(n.rect.x), y: Math.round(n.rect.y), w: r1(n.rect.w), h: n.rect.h });
  }
  // The end-card call to action goes on the company line if it fits, else the period line.
  const companyW = textWidth(`${model.company.name} (${model.company.ticker})`, 56, 800);
  const periodW = textWidth(model.period_display, 40, 500);
  const ctaW = textWidth(model.cta || "", 32, 700);
  out.header = { cta: companyW + 40 + ctaW <= SPAN ? "company" : periodW + 40 + ctaW <= SPAN ? "period" : "none" };
  if (out.header.cta === "none") out.warnings.push("no room for the call to action in the header");
  out.frame = { headerTop: SAFE.top_px, headerBottom, firstRow: rowY[0], lastRow: rowY[rows - 1], footerTop, x0: X0, x1: X1, segBase, flow: Math.round(flow) };
  return out;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const id = process.argv[2];
  if (!id) {
    console.error("usage: node scripts/layout.mjs <ID>");
    process.exit(2);
  }
  const dir = path.join(ROOT, "out", id, "build");
  const model = JSON.parse(fs.readFileSync(path.join(dir, "model.json"), "utf8"));
  const result = layout(model);
  fs.writeFileSync(path.join(dir, "layout.json"), JSON.stringify(result, null, 2) + "\n");
  console.log(`wrote out/${id}/build/layout.json (${result.nodes.length} nodes, ${result.links.length} links, ${result.labels.length} labels, ${result.rows} rows, flow ${result.frame.flow}px)${result.warnings.length ? " warnings: " + result.warnings.join("; ") : ""}`);
}
