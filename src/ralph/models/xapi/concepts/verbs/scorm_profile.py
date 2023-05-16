"""`Scorm Profile` verbs definitions."""

from typing import Dict, Optional

from ...base.verbs import BaseXapiVerb
from ...concepts.constants.scorm_profile import (
    VERB_COMPLETED_DISPLAY,
    VERB_COMPLETED_ID,
    VERB_INITIALIZED_DISPLAY,
    VERB_INITIALIZED_ID,
    VERB_INTERACTED_DISPLAY,
    VERB_INTERACTED_ID,
    VERB_TERMINATED_DISPLAY,
    VERB_TERMINATED_ID,
)
from ...constants import LANG_EN_US_DISPLAY


class CompletedVerb(BaseXapiVerb):
    """Pydantic model for completed `verb`.

    Attributes:
        id (str): Consists of the value `http://adlnet.gov/expapi/verbs/completed`.
        display (dict): Consists of the dictionary `{"en-US": "completed"}`.
    """

    id: VERB_COMPLETED_ID = VERB_COMPLETED_ID.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_COMPLETED_DISPLAY]]


class InitializedVerb(BaseXapiVerb):
    """Pydantic model for initialized `verb`.

    Attributes:
        id (str): Consists of the value `http://adlnet.gov/expapi/verbs/initialized`.
        display (Dict): Consists of the dictionary `{"en-US": "initialized"}`.
    """

    id: VERB_INITIALIZED_ID = VERB_INITIALIZED_ID.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_INITIALIZED_DISPLAY]]


class InteractedVerb(BaseXapiVerb):
    """Pydantic model for interacted `verb`.

    Attributes:
        id (str): Consists of the value `http://adlnet.gov/expapi/verbs/interacted`.
        display (dict): Consists of the dictionary `{"en-US": "interacted"}`.
    """

    id: VERB_INTERACTED_ID = VERB_INTERACTED_ID.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_INTERACTED_DISPLAY]]


class TerminatedVerb(BaseXapiVerb):
    """Pydantic model for terminated `verb`.

    Attributes:
        id (str): Consists of the value `http://adlnet.gov/expapi/verbs/terminated`.
        display (dict): Consists of the dictionary `{"en-US": "terminated"}`.
    """

    id: VERB_TERMINATED_ID = VERB_TERMINATED_ID.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_TERMINATED_DISPLAY]]
