"""Safe metadata and precomputed transcripts for synthetic audio fixtures."""

from dataclasses import dataclass
from pathlib import Path


VOICE_FIXTURES_ROOT = Path(__file__).resolve().parent.parent / "static" / "voice-fixtures"
MOCK_DISCLOSURE = "Mock transcript fixture - local ASR unavailable in this environment."


@dataclass(frozen=True)
class FixtureSegment:
    segment_index: int
    start_ms: int
    end_ms: int
    text: str


@dataclass(frozen=True)
class VoiceSample:
    sample_id: str
    label: str
    scope: str
    interaction_type: str
    audio_filename: str
    duration_ms: int
    segments: tuple[FixtureSegment, ...]

    @property
    def audio_path(self) -> Path:
        return VOICE_FIXTURES_ROOT / self.audio_filename

    @property
    def provider_disclosure(self) -> str:
        return MOCK_DISCLOSURE


PATIENT_SAMPLE = VoiceSample(
    sample_id="patient-follow-up",
    label="Synthetic patient follow-up",
    scope="patient",
    interaction_type="ai_patient_session_summary",
    audio_filename="patient_follow_up.wav",
    duration_ms=24_000,
    segments=(
        FixtureSegment(
            0,
            0,
            8_000,
            "This is a synthetic patient voice sample. I have a follow-up appointment next week,",
        ),
        FixtureSegment(
            1,
            8_000,
            16_000,
            "and I still have a question about the pending laboratory review.",
        ),
        FixtureSegment(
            2,
            16_000,
            24_000,
            "This recording contains no real patient information.",
        ),
    ),
)


CLINICAL_SAMPLE = VoiceSample(
    sample_id="nurse-follow-up",
    label="Synthetic nurse follow-up",
    scope="clinical",
    interaction_type="ai_nurse_consult_summary",
    audio_filename="nurse_follow_up.wav",
    duration_ms=24_000,
    segments=(
        FixtureSegment(
            0,
            0,
            8_000,
            "This is a synthetic nurse follow-up. The scheduled laboratory review",
        ),
        FixtureSegment(
            1,
            8_000,
            16_000,
            "remains pending and requires clinician review.",
        ),
        FixtureSegment(
            2,
            16_000,
            24_000,
            "No diagnosis or treatment recommendation was made in this recording.",
        ),
    ),
)


VOICE_SAMPLES: tuple[VoiceSample, ...] = (PATIENT_SAMPLE, CLINICAL_SAMPLE)


def get_voice_sample(sample_id: str) -> VoiceSample | None:
    return next((sample for sample in VOICE_SAMPLES if sample.sample_id == sample_id), None)
