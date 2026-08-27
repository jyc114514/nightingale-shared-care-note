# Phase 9 Voice capability probe - 2026-08-27

## Environment

- GPU: NVIDIA GeForce RTX 5070 Ti Laptop GPU
- Reported VRAM: 12,227 MiB total; 9,419 MiB free at probe start
- Driver: 596.13
- Torch: 2.11.0+cu128
- CUDA runtime reported by Torch: 12.8
- `torch.cuda.is_available()`: `True`
- Python: 3.10.20 in the pre-existing `ai_env`

## ASR attempt

The optional local dependency set was isolated in `backend/requirements.voice.in` and
`backend/requirements.voice.lock`. The installation added only these eight packages and did not
upgrade or remove existing packages:

- `av==17.1.0`
- `coloredlogs==15.0.1`
- `ctranslate2==4.8.1`
- `faster-whisper==1.2.1`
- `flatbuffers==25.12.19`
- `humanfriendly==10.0`
- `onnxruntime==1.23.2`
- `pyreadline3==3.5.6`

`pip check` passed after installation. The official faster-whisper implementation documents the
`turbo` alias and the `WhisperModel("turbo", device="cuda", compute_type="float16")` path;
the implementation was selected accordingly. A six-second deterministic tone WAV was used for a
hardware integration probe. Windows local TTS could not produce a usable spoken WAV, and the Turbo
model download stopped after approximately 3.8 MB of metadata with no forward progress, so no
functional speech transcript, WER, or Whisper success claim is made. No driver, system CUDA,
administrator, or microphone action was used.

## Achieved level

**Level C - Architecture/demo only:** prerecorded synthetic audio with mock transcript fixture;
ASR inference unavailable in this environment.

The repository contains two deterministic 24-second mono WAV fixtures and expected transcript
segments. The audio is synthetic signal data, not a recording of a person. The UI labels the
transcript as a mock fixture and confidence as unavailable. The optional faster-whisper adapter
remains lazy and injection-testable, but model weights are not committed or packaged.

Fixture hashes:

- `patient_follow_up.wav`: `f04b51156c1d3d769d1fe728cf9f4b16710ff3bc3301cc795e214f8753e98a6c`
- `nurse_follow_up.wav`: `d1f8a9cd1c4246e168e7eb37b734c55c14e0bc248ef07fa9851c0471c9c189d0`

The Voice path preserves clinic/patient authorization, immutable ordered transcript segments,
audio hash and duration metadata, source-segment linkage, fixture-first summary processing, safe
failure states, and metadata-only SSE. It does not implement microphone capture, diarization,
overlap/noise handling, multilingual clinical ASR, production PHI audio, or model-quality claims.

## Render Level-C enablement

The existing Render evaluation app now enables `VOICE_PROVIDER=fixture` while keeping
`LLM_PROVIDER=fixture`. The configuration deploy reached Live, and the final startup/health logs
show no Voice dependency/model download or ASR error. The available authenticated browser session
had expired before the online Voice flow could be rerun; local backend/frontend role/privacy tests
remain the evidence for prerecorded WAV playback, mock transcript, confidence-unavailable state,
source/provenance, and sample scoping. This is a **Partial Bonus / Level C** result, not full
Ambient Voice, until a user-authenticated online smoke is completed.
