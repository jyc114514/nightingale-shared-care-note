"""Fixture-first ASR protocol with a lazy optional faster-whisper adapter."""

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from app.voice.fixtures import VoiceSample


class VoiceProviderError(RuntimeError):
    """Safe error code for local ASR failures."""

    def __init__(self, error_code: str) -> None:
        super().__init__(error_code)
        self.error_code = error_code


@dataclass(frozen=True)
class ASRSegmentResult:
    segment_index: int
    start_ms: int
    end_ms: int
    text: str
    confidence: float | None


@dataclass(frozen=True)
class TranscriptResult:
    segments: tuple[ASRSegmentResult, ...]
    language: str
    language_probability: float | None
    word_timestamps_available: bool
    confidence_available: bool


class ASRProvider(Protocol):
    name: str
    model: str

    def transcribe(self, audio_path: Path, sample: VoiceSample) -> TranscriptResult:
        """Return ordered transcript metadata without logging raw text."""


class FixtureTranscriptProvider:
    name = "mock-transcript-fixture"
    model = "precomputed-v1"

    def transcribe(self, audio_path: Path, sample: VoiceSample) -> TranscriptResult:
        del audio_path
        return TranscriptResult(
            segments=tuple(
                ASRSegmentResult(
                    segment_index=segment.segment_index,
                    start_ms=segment.start_ms,
                    end_ms=segment.end_ms,
                    text=segment.text,
                    confidence=None,
                )
                for segment in sample.segments
            ),
            language="en",
            language_probability=None,
            word_timestamps_available=False,
            confidence_available=False,
        )


class FasterWhisperProvider:
    name = "faster-whisper"

    def __init__(
        self,
        *,
        model_id: str = "turbo",
        device: str = "cuda",
        compute_type: str = "float16",
        cache_dir: str | None = None,
        model: object | None = None,
        model_factory: Callable[[str, str, str, str | None], object] | None = None,
    ) -> None:
        self.model = model_id
        self.device = device
        self.compute_type = compute_type
        self.cache_dir = cache_dir
        self._model = model
        self._model_factory = model_factory

    def _load_model(self) -> object:
        if self._model is not None:
            return self._model
        if self._model_factory is not None:
            self._model = self._model_factory(
                self.model, self.device, self.compute_type, self.cache_dir
            )
            return self._model
        try:
            from faster_whisper import WhisperModel  # type: ignore[import-untyped]
        except ImportError as exc:
            raise VoiceProviderError("asr_dependency_missing") from exc
        try:
            self._model = WhisperModel(
                self.model,
                device=self.device,
                compute_type=self.compute_type,
                download_root=self.cache_dir,
            )
        except Exception as exc:
            raise VoiceProviderError("asr_model_unavailable") from exc
        return self._model

    def transcribe(self, audio_path: Path, sample: VoiceSample) -> TranscriptResult:
        del sample
        model = self._load_model()
        transcribe = cast(
            Callable[..., tuple[Iterable[object], object]], getattr(model, "transcribe")
        )
        try:
            raw_segments, info = transcribe(
                str(audio_path),
                language="en",
                vad_filter=True,
                word_timestamps=True,
                condition_on_previous_text=False,
                beam_size=5,
            )
            segments: list[ASRSegmentResult] = []
            word_timestamps_available = True
            confidence_available = True
            for index, raw_segment in enumerate(raw_segments):
                text = str(getattr(raw_segment, "text", "")).strip()
                words = getattr(raw_segment, "words", None)
                word_values = list(cast(Iterable[object], words)) if words is not None else []
                probabilities = [
                    float(probability)
                    for word in word_values
                    if (probability := getattr(word, "probability", None)) is not None
                ]
                if not word_values:
                    word_timestamps_available = False
                if not probabilities:
                    confidence_available = False
                start_ms = int(round(float(getattr(raw_segment, "start")) * 1000))
                end_ms = int(round(float(getattr(raw_segment, "end")) * 1000))
                segments.append(
                    ASRSegmentResult(
                        segment_index=index,
                        start_ms=start_ms,
                        end_ms=end_ms,
                        text=text,
                        confidence=(sum(probabilities) / len(probabilities))
                        if probabilities
                        else None,
                    )
                )
            language_probability = getattr(info, "language_probability", None)
            return TranscriptResult(
                segments=tuple(segments),
                language=str(getattr(info, "language", "en")),
                language_probability=(
                    float(language_probability) if language_probability is not None else None
                ),
                word_timestamps_available=word_timestamps_available,
                confidence_available=confidence_available,
            )
        except VoiceProviderError:
            raise
        except Exception as exc:
            raise VoiceProviderError("asr_inference_failed") from exc
