// Covers and carousel stills for one quarter.
//
//   node scripts/stills.mjs <ID>              # needs Gate A (approval hash must match)
//   node scripts/stills.mjs <ID> --preview    # private review copies, marked "Style preview"
//
// Writes out/<ID>/cover-9x16.png (the video's final frame), out/<ID>/cover-4x5.png and
// out/<ID>/carousel/01.png … 06.png (1080×1350). Same model, layout and theme as the video.

import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { layout } from "./layout.mjs";
import { approvalOk } from "./render.mjs";
import { buildHtml } from "../templates/money-map/composition.mjs";
import { SLIDE, coverSlide, dollarSlide, marginsSlide, segmentsSlide, sourcesSlide } from "../templates/carousel/slides.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const HF = path.join(ROOT, "node_modules", "hyperframes", "bin", "hyperframes.mjs");
const PY = path.join(ROOT, ".venv", "Scripts", "python.exe");
const ENV = { ...process.env, HYPERFRAMES_NO_TELEMETRY: "1", DO_NOT_TRACK: "1", HYPERFRAMES_NO_UPDATE_CHECK: "1", HYPERFRAMES_NO_AUTO_INSTALL: "1", HYPERFRAMES_SKIP_SKILLS: "1" };

function run(cmd, args) {
  const r = spawnSync(cmd, args, { cwd: ROOT, env: ENV, encoding: "utf8" });
  if (r.status !== 0) throw new Error(`${path.basename(cmd)} ${args.slice(0, 3).join(" ")} failed:\n${(r.stderr || r.stdout || "").slice(-1500)}`);
  return r.stdout;
}
const hf = (...a) => run(process.execPath, [HF, ...a]);

function snap(dir, at, dest) {
  const tmp = path.join(dir, "_snap");
  fs.rmSync(tmp, { recursive: true, force: true });
  hf("snapshot", dir, "--at", String(at), "-o", tmp, "--no-end", "--no-browser-gpu");
  const png = fs.readdirSync(tmp).find((f) => f.endsWith(".png") && f.startsWith("frame-"));
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  fs.copyFileSync(path.join(tmp, png), dest);
  fs.rmSync(tmp, { recursive: true, force: true });
}

function main() {
  const id = process.argv[2];
  const preview = process.argv.includes("--preview");
  if (!id || id.startsWith("--")) {
    console.error("usage: node scripts/stills.mjs <ID> [--preview]");
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
  const theme = tokens.themes[tokens.theme];
  run(PY, ["scripts/money_map_model.py", id]);
  const buildDir = path.join(ROOT, "out", id, "build");
  const model = JSON.parse(fs.readFileSync(path.join(buildDir, "model.json"), "utf8"));
  const outDir = path.join(ROOT, "out", id, preview ? "preview-stills" : "");
  const assets = (dir) => {
    fs.mkdirSync(path.join(dir, "assets"), { recursive: true });
    fs.copyFileSync(path.join(ROOT, tokens.font.files.variable), path.join(dir, "assets/InterVariable.woff2"));
    fs.copyFileSync(path.join(ROOT, "node_modules/gsap/dist/gsap.min.js"), path.join(dir, "assets/gsap.min.js"));
  };
  const mark = (html) => {
    if (!preview) return html;
    const i = html.lastIndexOf("</section>");
    return html.slice(0, i) + `<div style="position:absolute;z-index:9;left:72px;top:22px;font:600 24px Inter,sans-serif;color:${theme.accent}">Style preview. Not approved for publishing.</div>` + html.slice(i);
  };

  // 9:16 cover: the money map's final frame, rendered still (no hook, no call to action)
  const coverDir = path.join(buildDir, "cover-9x16");
  assets(coverDir);
  fs.writeFileSync(path.join(coverDir, "index.html"), mark(buildHtml({ model, layout: layout(model), theme, themeName: tokens.theme, tokens, still: true })));
  snap(coverDir, 0.5, path.join(outDir, "cover-9x16.png"));

  // carousel, 4:5
  const safe = { top_px: SLIDE.margin, bottom_px: SLIDE.margin, left_px: SLIDE.margin, right_px: SLIDE.margin };
  const mapLayout = layout(model, { width: SLIDE.width, height: SLIDE.height, safe, segments: false, headerGap: 40 });
  if (mapLayout.warnings.length) console.warn("carousel map warnings:\n  " + mapLayout.warnings.join("\n  "));
  const slides = [
    (n, t) => coverSlide(model, theme, n, t),
    (n, t) => {
      const html = buildHtml({ model, layout: mapLayout, theme, themeName: tokens.theme, tokens, still: true });
      const i = html.lastIndexOf("</section>");
      return html.slice(0, i) + `<div style="position:absolute;right:${SLIDE.margin}px;top:${SLIDE.margin + 6}px;font:600 26px Inter,sans-serif;color:${theme.ink_muted}">${n}/${t}</div>` + html.slice(i);
    },
    (n, t) => segmentsSlide(model, theme, n, t),
    (n, t) => marginsSlide(model, theme, n, t),
    (n, t) => dollarSlide(model, theme, n, t),
    (n, t) => sourcesSlide(model, theme, n, t),
  ];
  slides.forEach((make, i) => {
    const n = i + 1;
    const dir = path.join(buildDir, "carousel", String(n).padStart(2, "0"));
    assets(dir);
    fs.writeFileSync(path.join(dir, "index.html"), mark(make(n, slides.length)));
    hf("lint", dir);
    snap(dir, 0.5, path.join(outDir, "carousel", `${String(n).padStart(2, "0")}.png`));
  });
  fs.copyFileSync(path.join(outDir, "carousel", "01.png"), path.join(outDir, "cover-4x5.png"));
  console.log(`stills → ${path.relative(ROOT, outDir) || "out/" + id}: cover-9x16.png, cover-4x5.png, carousel/01–${String(slides.length).padStart(2, "0")}.png`);
}

main();
