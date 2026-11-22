#!/bin/bash
# Re-render frame ranges and splice them into out/molasses/video.mp4: bash scripts/patch.sh 270-352 462-492
# (then re-mux + QA: same last steps as assemble.sh). Resumable: finished patches are kept.
set -e
cd "$(dirname "$0")/.."
D=out/molasses; mkdir -p $D/patch
for r in "$@"; do
  p=$D/patch/p$r.mp4
  [ -s $p ] || { timeout 4000 node scripts/render.mjs MolassesShort $p.tmp.mp4 1.3333 $r ${CONC:-3} 2>&1 | grep -aE "^done|rror" | grep -v 404 | tail -2; mv $p.tmp.mp4 $p; }
done
# splice: base video split around each patch, re-encoded once on an even 30 fps timeline
args=(-i $D/video.mp4); fc=""; parts=""; prev=0; k=1; n=0
for r in "$@"; do
  a=${r%-*}; b=${r#*-}; args+=(-i $D/patch/p$r.mp4)
  fc+="[0:v]trim=start_frame=$prev:end_frame=$a,setpts=PTS-STARTPTS[s$n];[$k:v]setpts=PTS-STARTPTS[q$n];"
  parts+="[s$n][q$n]"; prev=$((b + 1)); k=$((k + 1)); n=$((n + 1))
done
fc+="[0:v]trim=start_frame=$prev,setpts=PTS-STARTPTS[s$n];${parts}[s$n]concat=n=$((2 * n + 1)):v=1:a=0,setpts=N/30/TB[v]"
ffmpeg -v error -y "${args[@]}" -filter_complex "$fc" -map "[v]" -r 30 -fps_mode cfr -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -movflags +faststart $D/video_patched.mp4
mv $D/video_patched.mp4 $D/video.mp4
ffmpeg -v error -y -i $D/video.mp4 -i ../shorts/molasses/audio/mix.wav -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 320k -ar 48000 -shortest $D/final.mp4
python3 scripts/molasses_shots.py
python3 scripts/short_qa.py $D/final.mp4 $D/qa $D/shots.json
