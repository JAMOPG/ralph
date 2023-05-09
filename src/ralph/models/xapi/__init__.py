"""xAPI pydantic models."""

# flake8: noqa

from .assessment.statements import (
    AssessmentCompleted,
    AssessmentInitialized,
    AssessmentLaunched,
    AssessmentTerminated,
)
from .navigation.statements import PageTerminated, PageViewed
from .video.statements import (
    VideoCompleted,
    VideoEnableClosedCaptioning,
    VideoInitialized,
    VideoPaused,
    VideoPlayed,
    VideoScreenChangeInteraction,
    VideoSeeked,
    VideoTerminated,
    VideoVolumeChangeInteraction,
)
