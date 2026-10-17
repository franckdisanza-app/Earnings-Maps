// Build and render a money map with HyperFrames.
//
//   node scripts/render.mjs <ID> --video                       # needs Gate A: approval hash must match
//   node scripts/render.mjs <ID> --preview --theme all --snapshot 1.2,9,21,29.9 [--video]
//
// Steps: view model (scripts/money_map_model.py) → layout (scripts/layout.mjs) → one HyperFrames
// project per theme in out/<ID>/build/<theme>/ (index.html + local GSAP + Inter) → snapshots
// and/or MP4. Without --preview the data file's SHA-256 must equal data/normalized/<ID>.approval.json,
// otherwise nothing renders. --preview output is marked "Style preview" and is for private review.

import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { layout } from "./layout.mjs";
import { buildHtml } from "../templates/money-map/composition.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const PY = path.join(ROOT, ".venv", "Scripts", "python.exe");
const HF_ENV = {
  ...process.env,
  HYPERFRAMES_NO_TELEMETRY: "1",
  DO_NOT_TRACK: "1",
  HYPERFRAMES_NO_UPDATE_CHECK: "1",
  HYPERFRAMES_NO_AUTO_INSTALL: "1",
  HYPERFRAMES_SKIP_SKILLS: "1",
};

function arg(name, fallback = null) {
  const i = process.argv.indexOf(name);
  return i > 0 && process.argv[i + 1] && !process.argv[i + 1].startsWith("--") ? process.argv[i + 1] : fallback;
}
const flag = (name) => process.argv.includes(name);

function run(cmd, args, opts = {}) {
  const r = spawnSync(cmd, args, { cwd: ROOT, env: HF_ENV, encoding: "utf8", shell: process.platform === "win32" && cmd === "npx", ...opts });
  if (r.status !== 0) {
    console.error(r.stdout?.slice(-2000) || "", r.stderr?.slice(-2000) || "");
    throw new Error(`${cmd} ${args.join(" ")} failed (${r.status})`);
  }
  return r.stdout;
}

export function approvalOk(id) {
  const data = path.join(ROOT, "data", "normalized", `${id}.json`);
  const appr = path.join(ROOT, "data", "normalized", `${id}.approval.json`);
  if (!fs.existsSync(appr)) return [false, `no approval for ${id} (Gate A not passed)`];
  const want = JSON.parse(fs.readFileSync(appr, "utf8")).sha256;
  const have = crypto.createHash("sha256").update(fs.readFileSync(data)).digest("hex");
  return have === want ? [true, "approved"] : [false, `${id} changed after approval; needs a new Gate A`];
}

function main() {
  const id = process.argv[2];
  if (!id || id.startsWith("--")) {
    console.error("usage: node scripts/render.mjs <ID> [--preview] [--theme <name>|all] [--snapshot t1,t2,...] [--video] [--quality draft|delivery]");
    process.exit(2);
  }
  const preview = flag("--preview");
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
  if (!preview && themes.length !== 1) {
    console.error("a final render needs exactly one theme (set it in brand/tokens.json after Gate 2)");
    process.exit(2);
  }

  run(PY, ["scripts/money_map_model.py", id]);
  const buildDir = path.join(ROOT, "out", id, "build");
  const model = JSON.parse(fs.readFileSync(path.join(buildDir, "model.json"), "utf8"));
  const geo = layout(model);
  fs.writeFileSync(path.join(buildDir, "layout.json"), JSON.stringify(geo, null, 2) + "\n");
  if (geo.warnings.length) console.warn("layout warnings:\n  " + geo.warnings.join("\n  "));

  const snapshot = arg("--snapshot");
  const video = flag("--video");
  const quality = arg("--quality", preview ? "draft" : "delivery");
  for (const name of themes) {
    const theme = tokens.themes[name];
    const dir = path.join(buildDir, name);
    fs.mkdirSync(path.join(dir, "assets"), { recursive: true });
    fs.copyFileSync(path.join(ROOT, "node_modules/gsap/dist/gsap.min.js"), path.join(dir, "assets/gsap.min.js"));
    fs.copyFileSync(path.join(ROOT, tokens.font.files.variable), path.join(dir, "assets/InterVariable.woff2"));
    fs.writeFileSync(path.join(dir, "index.html"), buildHtml({ model, layout: geo, theme, themeName: name, tokens, preview }));
    run("npx", ["hyperframes", "lint", dir]);
    console.log(`built ${path.relative(ROOT, dir)}`);
    if (snapshot) {
      const outDir = path.join(ROOT, "out", id, preview ? "style-frames" : "keyframes", name);
      fs.rmSync(outDir, { recursive: true, force: true });
      run("npx", ["hyperframes", "snapshot", dir, "--at", snapshot, "-o", outDir, "--no-end", "--no-browser-gpu"]);
      console.log(`snapshots → ${path.relative(ROOT, outDir)}`);
    }
    if (video) {
      const file = path.join(ROOT, "out", id, preview ? `preview-${name}.mp4` : "money-map.mp4");
      run("npx", ["hyperframes", "render", dir, "-o", file, "--fps", "30", "--quality", quality]);
      console.log(`video → ${path.relative(ROOT, file)}`);
    }
  }
}

main();
