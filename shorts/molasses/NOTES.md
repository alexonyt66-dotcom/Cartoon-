# The Great Molasses Flood — production notes

- Final: `project/out/molasses/final.mp4` (1440x2560, 30 fps, 2085 frames, 69.5 s, h264 crf 16 + AAC 320k). Not committed (size); rebuild with the steps below.
- Voice: ElevenLabs "Clark", eleven_multilingual_v2, pauses tightened + tempo 1.12 → `voice/voice.wav`, word times `voice/words.json`.
- Sound: `audio/molasses_audio.py` → `mix.wav` (-15.2 LUFS, -1.2 dBTP), original ragtime score + synthesized SFX, music ducked -3 dB under speech.
- Render (software GL only, ~16-25 s/frame at 2K): `CONC=3 bash project/scripts/render_chunks.sh 0..13` (resumable, timed halves with retry), then `bash project/scripts/assemble.sh` (re-encoded concat on an even 30 fps timeline — a stream-copy concat dropped 43 frames), then `bash project/scripts/patch.sh a-b ...` to re-render and splice ranges.
- QA (short_qa.py): no black / white / frozen / pop frames.
- Fixes made during final QA: ink-pass cleanup crash at the shot 4→5 change; shot 2 crane passing through the elevated deck (now a cut); painters lowered from the rim instead of popping in; shot 6 opened as a wide with the neighbours; shot 8 splash crowns follow the curved front.
- Final Opus max audit: all 16 beats read and match narration, no on-screen text. Nits left: a few faces cut at frame edges (f493-575, f1135-1205), hard cut swallowing the horse (f135-165), dusk molasses a little lilac (f1490-1530).
