// Visual QA for one quarter's built videos, before Gate B.
//
//   node scripts/qa.mjs <ID> [--format money-map|dollar-split|kpi-cards|all] [--preview]
//
// Run scripts/render.mjs first (it builds out/<ID>/build/…). For each format this:
//   1. snapshots keyframes at 0, 25, 50, 75 and 100% into out/<ID>/qa/<format>/ (plus a contact sheet)
//   2. runs `hyperframes check` (lint, runtime errors, overflow, overlap, WCAG contrast) and sorts
//      findings into issues and expected ones: during the insight beat the map is dimmed on purpose
//      and the insight panel fully covers some dimmed labels
//   3. checks the safe zone and the footer line widths from the measured geometry
//   4. checks the MP4 when one exists: 1080×1920, 30 fps, H.264 + AAC, length, size, loudness
// and writes out/<ID>/qa.md. Exit code 1 when anything needs fixing.

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { textWidth } from "./layout.mjs";
import { dollarGeometry, kpiGeometry } from "../templates/formats/formats.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const HF = path.join(ROOT, "node_modules", "hyperframes", "bin", "hyperframes.mjs");
const ENV = { ...process.env, HYPERFRAMES_NO_TELEMETRY: "1", DO_NOT_TRACK: "1", HYPERFRAMES_NO_UPDATE_CHECK: "1", HYPERFRAMES_NO_AUTO_INSTALL: "1", HYPERFRAMES_SKIP_SKILLS: "1" };
const LENGTH = { "money-map": [25, 35], "dollar-split": [15, 35], "kpi-cards": [15, 35] };
const LOUDNESS = { min: -18, max: -10, peak: -1 }; // integrated LUFS window for phone feeds; true peak ceiling in dBTP
const MAX_MB = 100;

function run(cmd, args, ok = [0]) {
  const r = spawnSync(cmd, args, { cwd: ROOT, env: ENV, encoding: "utf8", maxBuffer: 64 * 1024 * 1024 });
  if (!ok.includes(r.status)) throw new Error(`${path.basename(cmd)} ${args.slice(0, 3).join(" ")} failed (${r.status}):\n${(r.stderr || r.stdout || "").slice(-1500)}`);
  return r;
}
const hf = (...a) => run(process.execPath, [HF, ...a], [0, 1]);
const rel = (p) => path.relative(ROOT, p).replace(/\\/g, "/");

// ---- 2) hyperframes check, sorted -------------------------------------------------------------

function sortFindings(check, beats) {
  const insight = beats.find((b) => b.beat === "insight");
  const inInsight = (t) => insight && t >= insight.start && t <= insight.start + insight.dur;
  const focus = insight?.nodes?.[0];
  const issues = [];
  const expected = [];
  for (const area of ["lint", "runtime", "layout", "motion", "contrast"]) {
    for (const f of check[area]?.findings ?? []) {
      const t = f.time ?? f.times?.[0] ?? 0;
      const node = f.dataAttributes?.["data-node"];
      const line = `${area}: ${f.code} at ${t.toFixed?.(2) ?? t} s, ${f.selector ?? ""}${f.text ? ` "${f.text}"` : ""}${f.ratio ? ` (${f.ratio}:1)` : ""}${f.coveredFraction != null ? ` (${Math.round(f.coveredFraction * 100)}% covered)` : ""}`;
      if (f.code === "nested_structure_needs_subcomposition") expected.push(`${line}: studio timeline hint, no effect on the render`);
      else if (f.code === "text_occluded" && f.containerSelector === "#insight" && f.coveredFraction === 1 && inInsight(t)) expected.push(`${line}: dimmed label fully under the insight panel`);
      else if (f.code === "contrast_aa_failure" && inInsight(t) && node && node !== focus) expected.push(`${line}: dimmed on purpose during the insight beat`);
      else if (f.severity === "info") expected.push(`${line}: info`);
      else issues.push(`${line}: ${f.message ?? ""}`.trim());
    }
  }
  return { issues, expected };
}

// ---- 3) safe zone and footer, from the geometry the templates use ------------------------------

function safeZone(format, model, tokens, theme, buildDir) {
  const safe = tokens.safe_zone_9x16;
  const W = tokens.canvas.video.width;
  const H = tokens.canvas.video.height;
  const zone = { x0: safe.left_px, y0: safe.top_px, x1: W - safe.right_px, y1: H - safe.bottom_px };
  const boxes = [];
  const warnings = [];
  const textBox = (what, text, x, baseline, size, weight, anchor = "start") => {
    const w = textWidth(text, size, weight);
    const x0 = anchor === "end" ? x - w : anchor === "middle" ? x - w / 2 : x;
    boxes.push({ what, x0, x1: x0 + w, y0: baseline - size * 0.97, y1: baseline + size * 0.24 });
  };
  if (format === "money-map") {
    const lay = JSON.parse(fs.readFileSync(path.join(buildDir, "layout.json"), "utf8"));
    warnings.push(...lay.warnings);
    for (const n of lay.nodes) boxes.push({ what: `bar ${n.id}`, x0: n.x, x1: n.x + n.w, y0: n.y, y1: n.y + n.h });
    for (const t of lay.labels) textBox(`label "${t.text}"`, t.text, t.x, t.y, t.size, t.hero ? theme.style.hero_weight : t.weight >= 700 ? theme.style.value_weight : t.weight, t.anchor);
  } else if (format === "dollar-split") {
    const g = dollarGeometry(model, tokens, theme);
    warnings.push(...g.warnings);
    g.hookLines.forEach((l, i) => textBox(`hook "${l}"`, l, g.fr.x0, g.fr.hookTop + (i + 0.8) * g.fr.hook.lead, g.fr.hook.size, g.fr.hook.weight));
    for (const p of g.parts) {
      boxes.push({ what: `part ${p.label}`, x0: g.fr.x0, x1: g.labelX - 48, y0: p.y, y1: p.y + p.h });
      p.lines.forEach((l, i) => textBox(`label "${l}"`, l, g.labelX, p.ly + 88 + 6 + (i + 0.8) * 48, 40, 500));
    }
  } else {
    const g = kpiGeometry(model, tokens, theme);
    warnings.push(...g.warnings);
    g.hookLines.forEach((l, i) => textBox(`hook "${l}"`, l, g.fr.x0, g.fr.hookTop + (i + 0.8) * g.fr.hook.lead, g.fr.hook.size, g.fr.hook.weight));
    for (const c of g.cards) boxes.push({ what: `card ${c.label}`, x0: g.fr.x0, x1: g.fr.x1, y0: c.top, y1: c.top + g.cardH });
  }
  // footer: source line, then basis + disclaimer with the brand on the right; two lines at 30 px
  const width = zone.x1 - zone.x0;
  const row2 = `${model.basis_line}. ${model.disclaimer}.`;
  if (textWidth(model.source_line, 30, 400) > width) warnings.push(`footer source line wraps (${Math.round(textWidth(model.source_line, 30, 400))} px > ${width} px)`);
  if (textWidth(row2, 30, 400) + 24 + textWidth(tokens.brand.name, 30, 700) > width) warnings.push("footer basis/disclaimer line collides with the brand name");
  const footerTop = H - safe.bottom_px - 84;
  boxes.push({ what: "footer", x0: zone.x0, x1: zone.x1, y0: footerTop, y1: footerTop + 76 });
  const out = boxes.filter((b) => b.x0 < zone.x0 - 1 || b.x1 > zone.x1 + 1 || b.y0 < zone.y0 - 1 || b.y1 > zone.y1 + 1).map((b) => `${b.what} leaves the safe zone (${Math.round(b.x0)},${Math.round(b.y0)}–${Math.round(b.x1)},${Math.round(b.y1)})`);
  return { warnings, out };
}

// ---- 4) the MP4 ----------------------------------------------------------------------------------

function videoCheck(file, format) {
  if (!fs.existsSync(file)) return { file: null, issues: [], lines: ["no MP4 yet (render with --video)"] };
  const probe = JSON.parse(run("ffprobe", ["-v", "error", "-show_streams", "-show_format", "-of", "json", file]).stdout);
  const v = probe.streams.find((s) => s.codec_type === "video");
  const a = probe.streams.find((s) => s.codec_type === "audio");
  const dur = parseFloat(probe.format.duration);
  const mb = fs.statSync(file).size / 1e6;
  const [num, den] = (v?.r_frame_rate ?? "0/1").split("/").map(Number);
  const fps = num / den;
  const issues = [];
  if (!v || v.width !== 1080 || v.height !== 1920) issues.push(`video is ${v?.width}×${v?.height}, not 1080×1920`);
  if (Math.abs(fps - 30) > 0.01) issues.push(`frame rate ${fps.toFixed(2)}, not 30`);
  if (v?.codec_name !== "h264") issues.push(`video codec ${v?.codec_name}, not H.264`);
  if (v?.pix_fmt !== "yuv420p") issues.push(`pixel format ${v?.pix_fmt}, not yuv420p`);
  if (!a) issues.push("no audio track");
  else if (a.codec_name !== "aac") issues.push(`audio codec ${a.codec_name}, not AAC`);
  const [lo, hi] = LENGTH[format];
  if (dur < lo - 0.05 || dur > hi + 0.05) issues.push(`length ${dur.toFixed(1)} s, outside ${lo}–${hi} s`);
  if (mb > MAX_MB) issues.push(`file is ${mb.toFixed(1)} MB, over ${MAX_MB} MB`);
  let loud = "";
  if (a) {
    const log = run("ffmpeg", ["-hide_banner", "-nostats", "-i", file, "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr;
    const summary = log.slice(log.lastIndexOf("Summary:"));
    const I = parseFloat(summary.match(/I:\s+(-?[\d.]+) LUFS/)?.[1]);
    const peak = parseFloat(summary.match(/Peak:\s+(-?[\d.]+) dBFS/)?.[1]);
    loud = `, ${I} LUFS integrated, true peak ${peak} dBTP`;
    if (!(I >= LOUDNESS.min && I <= LOUDNESS.max)) issues.push(`loudness ${I} LUFS, outside ${LOUDNESS.min} to ${LOUDNESS.max}`);
    if (peak > LOUDNESS.peak) issues.push(`true peak ${peak} dBTP, above ${LOUDNESS.peak}`);
  }
  const lines = [`${rel(file)}: ${v?.width}×${v?.height}, ${fps.toFixed(0)} fps, ${v?.codec_name}/${v?.pix_fmt} + ${a?.codec_name ?? "no audio"}, ${dur.toFixed(2)} s, ${mb.toFixed(1)} MB${loud}`];
  return { file, issues, lines };
}

// ---- main ----------------------------------------------------------------------------------------

function qaFormat(id, format, preview, tokens, theme, model) {
  const buildDir = path.join(ROOT, "out", id, "build");
  const dir = path.join(buildDir, format === "money-map" ? tokens.theme : `${format}-${tokens.theme}`);
  const beatsFile = path.join(buildDir, `beats-${format}.json`);
  if (!fs.existsSync(path.join(dir, "index.html")) || !fs.existsSync(beatsFile)) {
    return { format, skipped: `not built; run: node scripts/render.mjs ${id}${preview ? " --preview" : ""} --format ${format}` };
  }
  const { duration, beats } = JSON.parse(fs.readFileSync(beatsFile, "utf8"));
  const html = fs.readFileSync(path.join(dir, "index.html"), "utf8");
  const issues = [];
  if (preview !== html.includes('id="preview"')) issues.push(preview ? "build is not marked as a preview" : "build still carries the preview marker; re-render without --preview");

  // 1) keyframes
  const qaDir = path.join(ROOT, "out", id, "qa", format);
  fs.rmSync(qaDir, { recursive: true, force: true });
  const times = [0.05, duration * 0.25, duration * 0.5, duration * 0.75, duration - 0.05].map((t) => t.toFixed(2));
  hf("snapshot", dir, "--at", times.join(","), "-o", qaDir, "--no-end", "--no-browser-gpu");
  const frames = fs.existsSync(qaDir) ? fs.readdirSync(qaDir).filter((f) => f.endsWith(".png") || f.endsWith(".jpg")).sort() : [];
  if (frames.filter((f) => f.startsWith("frame-")).length !== times.length) issues.push(`expected ${times.length} keyframes, got ${frames.length}`);

  // 2) hyperframes check
  const r = hf("check", dir, "--json", "--no-browser-gpu", "--frame-check");
  let check;
  try {
    check = JSON.parse(r.stdout);
  } catch {
    issues.push(`hyperframes check gave no JSON: ${(r.stderr || "").slice(-300)}`);
    check = {};
  }
  const sorted = sortFindings(check, beats);
  issues.push(...sorted.issues);

  // 3) geometry
  const zone = safeZone(format, model, tokens, theme, buildDir);
  issues.push(...zone.warnings.map((w) => `layout: ${w}`), ...zone.out);

  // 4) video
  const base = format === "money-map" ? (preview ? tokens.theme : "money-map") : format;
  const video = videoCheck(path.join(ROOT, "out", id, preview ? `preview-${base}.mp4` : `${base}.mp4`), format);
  issues.push(...video.issues);

  return { format, duration, beats: beats.length, times, qaDir, frames, issues, expected: sorted.expected, video };
}

function main() {
  const id = process.argv[2];
  if (!id || id.startsWith("--")) {
    console.error("usage: node scripts/qa.mjs <ID> [--format money-map|dollar-split|kpi-cards|all] [--preview]");
    process.exit(2);
  }
  const i = process.argv.indexOf("--format");
  const which = i > 0 ? process.argv[i + 1] : "all";
  const formats = which === "all" ? Object.keys(LENGTH) : [which];
  if (!formats.every((f) => LENGTH[f])) {
    console.error(`unknown --format ${which}`);
    process.exit(2);
  }
  const preview = process.argv.includes("--preview");
  const tokens = JSON.parse(fs.readFileSync(path.join(ROOT, "brand/tokens.json"), "utf8"));
  const theme = tokens.themes[tokens.theme];
  const model = JSON.parse(fs.readFileSync(path.join(ROOT, "out", id, "build", "model.json"), "utf8"));

  const results = formats.map((f) => {
    if (f === "dollar-split" && !model.formats?.dollar_split) return { format: f, skipped: "no cents split for this quarter (a step is negative)" };
    process.stdout.write(`qa ${f}… `);
    const res = qaFormat(id, f, preview, tokens, theme, model);
    console.log(res.skipped ? "skipped" : res.issues.length ? `${res.issues.length} to fix` : "pass");
    return res;
  });

  const md = [`# Visual QA: ${model.company.name} ${model.period_display}`, "", `${id}${preview ? ", preview build" : ""}. Generated by \`node scripts/qa.mjs\`; frames in \`out/${id}/qa/\`.`, ""];
  for (const r of results) {
    md.push(`## ${r.format}`, "");
    if (r.skipped) {
      md.push(`Skipped: ${r.skipped}.`, "");
      continue;
    }
    md.push(`**${r.issues.length ? `${r.issues.length} to fix` : "Pass"}.** ${r.beats} beats, ${r.duration} s. Keyframes at ${r.times.join(", ")} s: \`${rel(r.qaDir)}/\` (contact sheet included).`, "");
    md.push("Video: " + r.video.lines.join("; "), "");
    if (r.issues.length) md.push("To fix:", "", ...r.issues.map((x) => `- ${x}`), "");
    if (r.expected.length) md.push(`Expected findings (${r.expected.length}):`, "", ...r.expected.map((x) => `- ${x}`), "");
  }
  const file = path.join(ROOT, "out", id, "qa.md");
  fs.writeFileSync(file, md.join("\n"));
  console.log(`report → ${rel(file)}`);
  const failed = results.some((r) => !r.skipped && r.issues.length);
  process.exit(failed ? 1 : 0);
}

main();
