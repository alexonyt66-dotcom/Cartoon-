#!/bin/bash
# Renders the molasses short at 2K in chunks (resumable): bash scripts/render_chunks.sh <chunk index...>
cd "$(dirname "$0")/.."
mkdir -p out/molasses/chunks
for i in "$@"; do
  a=$((i * 150)); b=$((a + 149)); [ $b -gt 2084 ] && b=2084
  o=out/molasses/chunks/c$i.mp4
  [ -s $o ] && { echo "skip $i"; continue; }
  node scripts/render.mjs MolassesShort $o.tmp.mp4 1.3333 $a-$b ${CONC:-2} 2>&1 | grep -aE "^frames|^done|rror" | tail -3
  [ -s $o.tmp.mp4 ] && mv $o.tmp.mp4 $o && echo "chunk $i ok"
done
