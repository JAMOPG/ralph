"""`TinCan Vocabulary` verbs definitions."""

from typing import Dict, Optional

from ...base.verbs import BaseXapiVerb
from ...constants import LANG_EN_US_DISPLAY
from ..constants.tincan_vocabulary import VERB_VIEWED_DISPLAY, VERB_VIEWED_ID


class ViewedVerb(BaseXapiVerb):
    """Pydantic model for viewed `verb`.

    Attributes:
        id (str): Consists of the value `http://id.tincanapi.com/verb/viewed`.
        display (dict): Consists of the dictionary `{"en-US": "viewed"}`.
    """

    id: VERB_VIEWED_ID = VERB_VIEWED_ID.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_VIEWED_DISPLAY]]
