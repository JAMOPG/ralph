"""`Video` verbs definitions."""

from typing import Dict

from ...base.verbs import BaseXapiVerb
from ...constants import LANG_EN_US_DISPLAY
from ..constants.video import (
    VERB_PAUSED_DISPLAY,
    VERB_PLAYED_DISPLAY,
    VERB_SEEKED_DISPLAY,
    VERB_VIDEO_PAUSED_ID,
    VERB_VIDEO_PLAYED_ID,
    VERB_VIDEO_SEEKED_ID,
)


class PlayedVerb(BaseXapiVerb):
    """Pydantic model for played `verb`.

    Attributes:
        id (str): Consists of the value `https://w3id.org/xapi/video/verbs/played`.
        display (dict): Consists of the dictionary `{"en-US": "played"}`.
    """

    id: VERB_VIDEO_PLAYED_ID = VERB_VIDEO_PLAYED_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, VERB_PLAYED_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: VERB_PLAYED_DISPLAY.__args__[0]
    }


class PausedVerb(BaseXapiVerb):
    """Pydantic model for paused `verb` field.

    Attributes:
        id (str): Consists of the value `https://w3id.org/xapi/video/verbs/paused`.
        display (dict): Consists of the dictionary `{"en-US": "paused"}`.
    """

    id: VERB_VIDEO_PAUSED_ID = VERB_VIDEO_PAUSED_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, VERB_PAUSED_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: VERB_PAUSED_DISPLAY.__args__[0]
    }


class SeekedVerb(BaseXapiVerb):
    """Pydantic model for seeked `verb` field.

    Attributes:
        id (str): Consists of the value `https://w3id.org/xapi/video/verbs/seeked`.
        display (dict): Consists of the dictionary `{"en-US": "seeked"}`.
    """

    id: VERB_VIDEO_SEEKED_ID = VERB_VIDEO_SEEKED_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, VERB_SEEKED_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: VERB_SEEKED_DISPLAY.__args__[0]
    }
