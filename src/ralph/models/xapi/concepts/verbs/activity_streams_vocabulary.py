"""`Activity streams vocabulary` verbs definitions."""

from typing import Dict, Optional

from ...base.verbs import BaseXapiVerb
from ...constants import LANG_EN_US_DISPLAY
from ..constants.activity_streams_vocabulary import (
    VERB_DISPLAY_JOINED,
    VERB_DISPLAY_LEFT,
    VERB_ID_JOIN,
    VERB_ID_LEAVE,
)


class JoinVerb(BaseXapiVerb):
    """Pydantic model for join verb.

    Attributes:
        id (str): Consists of the value `http://activitystrea.ms/join`.
        display (dict): Consists of the dictionary `{"en-US": "joined"}`.
    """

    id: VERB_ID_JOIN = VERB_ID_JOIN.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_DISPLAY_JOINED]]


class LeaveVerb(BaseXapiVerb):
    """Pydantic model for leave `verb`.

    Attributes:
        id (str): Consists of the value `http://activitystrea.ms/leave`.
        display (dict): Consists of the dictionary `{"en-US": "left"}`.
    """

    id: VERB_ID_LEAVE = VERB_ID_LEAVE.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_DISPLAY_LEFT]]
