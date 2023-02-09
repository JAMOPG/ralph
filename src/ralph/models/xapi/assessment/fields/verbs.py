"""Assessment xAPI events verb fields definitions."""

from typing import Dict

from ...constants import LANG_EN_US_DISPLAY, VERB_ANSWERED_DISPLAY, VERB_ANSWERED_ID
from ...fields.verbs import VerbField


class AnsweredVerbField(VerbField):
    """Pydantic model for answered `verb` field.

    Attributes:
        id (str): Consists of the value `http://adlnet.gov/expapi/verbs/answered`.
        display (Dict): Consists of the dictionary `{"en-US": "answered"}`.
    """

    id: VERB_ANSWERED_ID = VERB_ANSWERED_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, VERB_ANSWERED_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: VERB_ANSWERED_DISPLAY.__args__[0]
    }
