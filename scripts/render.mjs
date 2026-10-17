// Build and render a money map with HyperFrames.
//
//   node scripts/render.mjs <ID> --video                         # needs Gate A: approval hash must match
//   node scripts/render.mjs <ID> --preview [--snapshot 1.2,9,29.9] [--video] [--no-voice]
//   --format money-map (default) | dollar-split | kpi-cards   picks the template and its voice lines
//
// Steps: view model (scripts/money_map_model.py) → layout (scripts/layout.mjs) → voiceover (one
// Kokoro line per beat, cached by text, durations measured with ffprobe) → beat timings (each beat
// lasts at least as long as its line; the whole video is held to 25–35 s) → one HyperFrames
// project in out/<ID>/build/<theme>/ → snapshots and/or MP4.
// Without --preview the data file's SHA-256 must equal data/normalized/<ID>.approval.json,
// otherwise nothing renders. --preview output is marked "Style preview" and is for private review.

import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { layout } from "./layout.mjs";
import { writeScript } from "./script_sheet.mjs";
import { buildHtml } from "../templates/money-map/composition.mjs";
import { dollarSplitHtml, kpiCardsHtml } from "../templates/formats/formats.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PY = path.join(ROOT, ".venv", "Scripts", "python.exe");
const HF = path.join(ROOT, "node_modules", "hyperframes", "bin", "hyperframes.mjs");
const HF_ENV = {
  ...process.env,
  HYPERFRAMES_NO_TELEMETRY: "1",
  DO_NOT_TRACK: "1",
  HYPERFRAMES_NO_UPDATE_CHECK: "1",
  HYPERFRAMES_NO_AUTO_INSTALL: "1",
  HYPERFRAMES_SKIP_SKILLS: "1",
};
export const BEAT_MIN = { hook: 2.4, row: 2.4, insight: 4.2, end: 3.4, part: 2.2, card: 2.4 };
const LIMITS = { min: 25, max: 35 };
// voice lines and output names per format; the two short formats run 15–35 s
export const FORMATS = {
  "money-map": { voice: (m) => m.voice, min: LIMITS.min },
  "dollar-split": { voice: (m) => m.formats?.dollar_split?.voice, min: 15 },
  "kpi-cards": { voice: (m) => m.formats?.kpi_cards?.voice, min: 15 },
};

function arg(name, fallback = null) {
  const i = process.argv.indexOf(name);
  return i > 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[i + 1] : fallback;
}
const flag = (name) => process.argv.includes(name);

function run(cmd, args) {
  const r = spawnSync(cmd, args, { cwd: ROOT, env: HF_ENV, encoding: "utf8" });
  if (r.status !== 0) {
    console.error((r.stdout || "").slice(-2000), (r.stderr || "").slice(-2000));
    throw new Error(`${path.basename(cmd)} ${args.slice(0, 3).join(" ")} failed (${r.status})`);
  }
  return r.stdout;
}
const hf = (...args) => run(process.execPath, [HF, ...args]);

export function approvalOk(id) {
  const data = path.join(ROOT, "data", "normalized", `${id}.json`);
  const appr = path.join(ROOT, "data", "normalized", `${id}.approval.json`);
  if (!fs.existsSync(appr)) return [false, `no approval for ${id} (Gate A not passed)`];
  const want = JSON.parse(fs.readFileSync(appr, "utf8")).sha256;
  const have = crypto.createHash("sha256").update(fs.readFileSync(data)).digest("hex");
  return have === want ? [true, "approved"] : [false, `${id} changed after approval; needs a new Gate A`];
}

// Each clip is brought to the same loudness (two-pass linear loudnorm, true peak capped), so the
// voice sits near the -14 LUFS that phone feeds play at and no line is louder than the next.
export const VOICE_LOUDNESS = { I: -15, TP: -1.5, LRA: 11 };

function normalize(raw, out) {
  const { I, TP, LRA } = VOICE_LOUDNESS;
  const target = `I=${I}:TP=${TP}:LRA=${LRA}`;
  const r = spawnSync("ffmpeg", ["-hide_banner", "-nostats", "-i", raw, "-af", `loudnorm=${target}:print_format=json`, "-f", "null", "-"], { encoding: "utf8" });
  const m = JSON.parse(r.stderr.slice(r.stderr.lastIndexOf("{"), r.stderr.lastIndexOf("}") + 1));
  const measured = `measured_I=${m.input_i}:measured_TP=${m.input_tp}:measured_LRA=${m.input_lra}:measured_thresh=${m.input_thresh}:offset=${m.target_offset}`;
  run("ffmpeg", ["-v", "error", "-y", "-i", raw, "-af", `loudnorm=${target}:${measured}:linear=true`, "-ar", "24000", "-ac", "1", out]);
}

function synthesize(lines, voDir, voice, speed) {
  fs.mkdirSync(voDir, { recursive: true });
  const { I, TP } = VOICE_LOUDNESS;
  return lines.map((b) => {
    const key = crypto.createHash("sha256").update(`${voice}|${speed}|${b.text}`).digest("hex").slice(0, 16);
    const raw = path.join(voDir, `${key}.wav`);
    const file = path.join(voDir, `${key}.i${-I}tp${-TP}.wav`);
    if (!fs.existsSync(raw)) hf("tts", b.text, "-v", voice, "-s", String(speed), "-o", raw);
    if (!fs.existsSync(file)) normalize(raw, file);
    const duration = parseFloat(run("ffprobe", ["-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", file]));
    return { ...b, file, duration };
  });
}

export function planBeats(voiced, silent = false, minTotal = LIMITS.min) {
  let t = 0;
  const beats = voiced.map((b) => {
    const dur = Math.max(BEAT_MIN[b.beat], silent ? 0 : b.duration + 0.35);
    const out = { beat: b.beat, nodes: b.nodes, text: b.text, start: Math.round(t * 100) / 100, dur: Math.round(dur * 100) / 100, file: b.file, audio: silent ? 0 : b.duration };
    t += dur;
    return out;
  });
  // short videos: give the extra time to the end card (the screenshot frame), up to the minimum
  const total = beats.reduce((a, b) => a + b.dur, 0);
  if (total < minTotal) beats.at(-1).dur = Math.round((beats.at(-1).dur + minTotal - total) * 100) / 100;
  return beats;
}

function main() {
  const id = process.argv[2];
  if (!id || id.startsWith("--")) {
    console.error("usage: node scripts/render.mjs <ID> [--preview] [--theme <name>] [--snapshot t1,t2,...] [--video] [--quality draft|delivery] [--no-voice] [--format money-map|dollar-split|kpi-cards]");
    process.exit(2);
  }
  const preview = flag("--preview");
  const format = arg("--format", "money-map");
  if (!FORMATS[format]) {
    console.error(`unknown --format ${format}; one of ${Object.keys(FORMATS).join(", ")}`);
    process.exit(2);
  }
  if (!preview) {
    const [ok, why] = approvalOk(id);
    if (!ok) {
      console.error(`refusing to render: ${why}`);
      process.exit(1);
    }
  }
  const tokens = JSON.parse(fs.readFileSync(path.join(ROOT, "brand/tokens.json"), "utf8"));
  const themeArg = arg("--theme", tokens.status === "draft" ? "all" : tokens.theme);
  const themes = themeArg === "all" ? Object.keys(tokens.themes) : [themeArg];
  if (!preview && (themes.length !== 1 || tokens.status !== "final")) {
    console.error("a final render needs the Gate 2 theme (brand/tokens.json status: final)");
    process.exit(2);
  }

  run(PY, ["scripts/money_map_model.py", id]);
  const buildDir = path.join(ROOT, "out", id, "build");
  const model = JSON.parse(fs.readFileSync(path.join(buildDir, "model.json"), "utf8"));
  const geo = layout(model);
  fs.writeFileSync(path.join(buildDir, "layout.json"), JSON.stringify(geo, null, 2) + "\n");
  if (geo.warnings.length) console.warn("layout warnings:\n  " + geo.warnings.join("\n  "));

  // Voiceover and beat timings; speed the voice up a little if the video would run past 35 s.
  const lines = FORMATS[format].voice(model);
  if (!lines) {
    console.error(`${id} has no ${format} data (the cents split needs every step positive)`);
    process.exit(1);
  }
  const silent = flag("--no-voice") || !tokens.voice?.voice;
  let speed = tokens.voice?.speed || 1.0;
  let beats;
  for (;;) {
    const voiced = silent ? lines.map((b) => ({ ...b, duration: 0 })) : synthesize(lines, path.join(buildDir, "vo"), tokens.voice.voice, speed);
    beats = planBeats(voiced, silent, FORMATS[format].min);
    const total = beats.reduce((a, b) => a + b.dur, 0);
    if (total <= LIMITS.max || silent || speed >= 1.16) {
      if (total > LIMITS.max) console.warn(`video is ${total.toFixed(1)} s, over ${LIMITS.max} s; shorten the voice lines`);
      break;
    }
    speed = Math.round((speed + 0.08) * 100) / 100;
    console.log(`voice runs ${total.toFixed(1)} s; retrying at speed ${speed}`);
  }
  const duration = Math.round(beats.reduce((a, b) => a + b.dur, 0) * 100) / 100;
  fs.writeFileSync(path.join(buildDir, `beats-${format}.json`), JSON.stringify({ format, speed, duration, beats }, null, 2) + "\n");
  console.log(`beats: ${beats.length}, ${duration} s${silent ? " (no voice)" : `, voice ${tokens.voice.voice} at ${speed}`}`);
  writeScript(ROOT, id);

  const snapshot = arg("--snapshot");
  const video = flag("--video");
  const quality = arg("--quality", preview ? "draft" : "delivery");
  for (const name of themes) {
    const theme = tokens.themes[name];
    const dir = path.join(buildDir, format === "money-map" ? name : `${format}-${name}`);
    fs.rmSync(path.join(dir, "assets", "vo"), { recursive: true, force: true });
    fs.mkdirSync(path.join(dir, "assets", "vo"), { recursive: true });
    fs.copyFileSync(path.join(ROOT, "node_modules/gsap/dist/gsap.min.js"), path.join(dir, "assets/gsap.min.js"));
    fs.copyFileSync(path.join(ROOT, tokens.font.files.variable), path.join(dir, "assets/InterVariable.woff2"));
    const placed = beats.map((b, i) => {
      if (!b.file || silent) return { ...b, src: null };
      fs.copyFileSync(b.file, path.join(dir, "assets", "vo", `${i}.wav`));
      return { ...b, src: `assets/vo/${i}.wav` };
    });
    const html =
      format === "money-map"
        ? buildHtml({ model, layout: geo, theme, themeName: name, tokens, preview, beats: placed, duration })
        : (format === "dollar-split" ? dollarSplitHtml : kpiCardsHtml)({ model, theme, tokens, preview, beats: placed, duration });
    fs.writeFileSync(path.join(dir, "index.html"), html);
    hf("lint", dir);
    console.log(`built ${path.relative(ROOT, dir)}`);
    if (snapshot) {
      const outDir = path.join(ROOT, "out", id, preview ? "style-frames" : "keyframes", format === "money-map" ? name : format);
      fs.rmSync(outDir, { recursive: true, force: true });
      const times = snapshot === "beats" ? beats.map((b) => (b.start + b.dur - 0.1).toFixed(2)).join(",") : snapshot;
      hf("snapshot", dir, "--at", times, "-o", outDir, "--no-end", "--no-browser-gpu");
      console.log(`snapshots → ${path.relative(ROOT, outDir)}`);
    }
    if (video) {
      const base = format === "money-map" ? (preview ? name : "money-map") : format;
      const file = path.join(ROOT, "out", id, preview ? `preview-${base}.mp4` : `${base}.mp4`);
      hf("render", dir, "-o", file, "--fps", "30", "--quality", quality);
      console.log(`video → ${path.relative(ROOT, file)}`);
    }
  }
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
