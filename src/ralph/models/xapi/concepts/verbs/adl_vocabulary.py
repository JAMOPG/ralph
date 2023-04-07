"""`ADL Vocabulary` verbs definitions."""

from typing import Dict, Optional

from ...base.verbs import BaseXapiVerb
from ...constants import LANG_EN_US_DISPLAY
from ..constants.adl_vocabulary import (
    VERB_DISPLAY_ANSWERED,
    VERB_DISPLAY_ASKED,
    VERB_ID_ANSWERED,
    VERB_ID_ASKED,
)


class AskedVerb(BaseXapiVerb):
    """Pydantic model for asked `verb`.

    Attributes:
        id (str): Consists of the value `http://adlnet.gov/expapi/verbs/asked`.
        display (dict): Consists of the dictionary `{"en-US": "asked"}`.
    """

    id: VERB_ID_ASKED = VERB_ID_ASKED.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_DISPLAY_ASKED]]


class AnsweredVerb(BaseXapiVerb):
    """Pydantic model for answered `verb`.

    Attributes:
        id (str): Consists of the value `http://adlnet.gov/expapi/verbs/answered`.
        display (dict): Consists of the dictionary `{"en-US": "answered"}`.
    """

    id: VERB_ID_ANSWERED = VERB_ID_ANSWERED.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_DISPLAY_ANSWERED]]
