"""`Video` activity types definitions."""

from typing import Dict, Optional

from ...base.unnested_objects import (
    BaseXapiActivityType,
    BaseXapiActivityTypeDefinition,
)
from ...constants import LANG_EN_US_DISPLAY
from ..constants.video import VIDEO_OBJECT_DEFINITION_TYPE

# Video


class VideoActivityTypeDefinition(BaseXapiActivityTypeDefinition):
    """Pydantic model for video `Activity` type `definition` property.

    Attributes:
        type (str): Consists of the value
            `https://w3id.org/xapi/video/activity-type/video`.
    """

    type: VIDEO_OBJECT_DEFINITION_TYPE = VIDEO_OBJECT_DEFINITION_TYPE.__args__[0]


class VideoActivityType(BaseXapiActivityType):
    """Pydantic model for video `Activity` type.

    WARNING: Contains an optional name property, this is not a violation of
    conformity but goes against xAPI specification recommendations.

    Attributes:
        name (dict): Consists of the dictionary `{"en-US": <name of the video>}`.
        definition (dict): See VideoActivityTypeDefinition.
    """

    name: Optional[Dict[LANG_EN_US_DISPLAY, str]]
    definition: VideoActivityTypeDefinition = VideoActivityTypeDefinition()
