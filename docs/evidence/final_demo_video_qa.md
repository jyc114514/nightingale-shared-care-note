# Final demo video QA - 2026-08-28

Status: **content review incomplete; do not mark DEL-05 passed from this record**.

The original MP4 was kept in place and was not renamed, edited, cropped, transcoded, compressed,
subtitled, rewrapped, or added to Git. The user asked Codex to stop further video inspection during
this release pass, so this record deliberately separates machine checks from the remaining human
review.

## Original artifact

| Field | Observed value |
| --- | --- |
| File name | `新标签页 - Google Chrome 2026-08-28 11-37-05.mp4` |
| Size | 231,072,706 bytes |
| SHA-256 | `E85F8D7DA70BF258768F1EFC71A8CB7418D52D080B1449F85DBB9EF32B10F002` |
| Duration | 00:10:39.00 |
| Video | H.264 Main, 2560x1380, reported average 10.24 fps |
| Audio | AAC-LC, stereo, 48 kHz |
| Container | MP4 (`mp42`) |

## Machine checks completed

- FFmpeg 7.1 decoded the complete video and audio streams to a null output with exit code 0.
- The decoder reported no fatal error. It emitted non-monotonic-DTS warnings while validating the
  source timestamps; the original file was not rewritten.
- The audio stream was decoded for the complete duration. Volume analysis reported mean `-19.0 dB`
  and max `-0.0 dB`.
- The size and SHA-256 above were computed before packaging work. They must be recomputed after
  packaging and must remain identical.

## Human review still required

The following were not marked passed in this Codex run:

- complete human playback from first frame to last;
- English narration intelligibility and synchronization with the visible actions;
- Staff → Clinician → Patient order and coverage of Glance, provenance, Voice, collaboration, tasks,
  revision/history, and privacy;
- absence of readable password/API-key/credential content, private browser material, or real PHI;
- absence of misleading login, loading, error, or accidental-cut footage;
- final suitability of the observed 10:39 duration against the planned 4:40–4:55 recording guide.

The final MP4 is **not uploaded to GitHub**. Its original bytes are intended to be included once in
the submission ZIP only after the user completes the remaining content review. The test password is
not recorded here and is supplied manually in the submission email.
