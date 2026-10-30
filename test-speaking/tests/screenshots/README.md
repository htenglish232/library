# Classroom presentation review

Screenshots captured from the actual Unit 5 application in official Chrome, with native container Fullscreen API. These are review artifacts, not pixel-snapshot assertions. No lesson data was modified for these screenshots.

| Screen | Screenshot |
| --- | --- |
| Practice, answer visible | [Practice](practice.png) |
| Test, answer hidden | [Test](test.png) |
| Fullscreen Practice, 1920×1080 | [Fullscreen Practice](fullscreen-practice.png) |
| Fullscreen Test, 1920×1080 | [Fullscreen Test](fullscreen-test.png) |
| Fullscreen portrait, 390×844 | [Portrait](fullscreen-portrait.png) |

Both Chrome 156.0.8078.79 and Edge 142.0.3595.94 passed the presentation browser suite. Their reports are included here. The browsers were extracted from their official packages after signed repository metadata and SHA-256 verification, without root installation. Tested 1920×1080, 1366×768, and 390×844; fullscreen/navigation containment, Practice/Test answer behavior, random order stability, repeat-input lock, reduced motion, long text, local Noto Sans loading, speech cancellation and no microphone access.

Audio was instrumented to verify calls/cancellation; actual speaker/TTS quality and physical TV/projector output still need classroom hardware. All files in `tests/` are excluded from the deployable website artifact.
