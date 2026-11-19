// main.ts — entrypoint for the news-image-20261119 poster.
// The poster itself is rendered by generate.py (Python + PIL) and committed
// as entry.png next to this file. This program only moves that image into
// the harness output directory, refusing to ship anything over the 1 MiB
// cap. Node 22, standard library only, no network.
import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const SOURCE_NAME = "entry.png";
const OUTPUT_NAME = "entry.png";
const MAX_BYTES = 1024 * 1024; // kit limit: PNG/JPEG at most 1 MiB

// The repository root is the directory this file lives in.
function entryDir(): string {
  return dirname(fileURLToPath(import.meta.url));
}

// The harness tells us where to write via MAKEFUN_OUTPUT_DIR; the kit's
// documented default is the absolute /output directory.
function outputDir(): string {
  const fromEnv = process.env.MAKEFUN_OUTPUT_DIR;
  if (fromEnv && fromEnv.length > 0) return resolve(fromEnv);
  return "/output";
}

function sha256(path: string): string {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function main(): void {
  const source = join(entryDir(), SOURCE_NAME);
  if (!existsSync(source)) {
    throw new Error(`missing source image: ${source}`);
  }
  const size = statSync(source).size;
  if (size > MAX_BYTES) {
    throw new Error(`source image ${size} bytes exceeds the ${MAX_BYTES} byte cap`);
  }
  const outDir = outputDir();
  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, OUTPUT_NAME);
  copyFileSync(source, target);
  const copied = statSync(target).size;
  if (copied !== size) {
    throw new Error(`copy mismatch: wrote ${copied} bytes, expected ${size}`);
  }
  console.log(
    `wrote ${target} (${copied} bytes, sha256 ${sha256(target)})`,
  );
}

try {
  main();
} catch (err) {
  console.error(`main.ts failed: ${err instanceof Error ? err.message : err}`);
  process.exit(1);
}
