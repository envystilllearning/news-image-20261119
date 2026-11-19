// news-image-20261119 entry (Node 22, standard library only).
//
// The poster is entry.png beside this file: a light one-page newspaper
// (1024x1024) that sums up Thursday 19 November 2026 in 40 verified
// stories, drawn in code by generate.py (Pillow, run locally). This program
// only places an exact copy of it at /output/entry.png, so the run is
// trivially deterministic: the same bytes in, the same bytes out. The gate
// allows at most 1 MiB and 1024 by 1024 pixels; the poster is 1024x1024 and
// well under the size cap.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, 'entry.png');
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, 'entry.png');

if (!existsSync(source)) {
  throw new Error(`entry image missing: ${source}`);
}
mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

// Guard against a partial copy: the judge reads exactly these bytes.
if (statSync(source).size !== statSync(target).size) {
  throw new Error(`copy incomplete: ${source} -> ${target}`);
}
