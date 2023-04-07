"""`AcrossX Profile` verbs definitions."""

from typing import Dict, Optional

from ...base.verbs import BaseXapiVerb
from ...constants import LANG_EN_US_DISPLAY
from ..constants.acrossx_profile import VERB_DISPLAY_POSTED, VERB_ID_POSTED


class PostedVerb(BaseXapiVerb):
    """Pydantic model for posted `verb`.

    Attributes:
        id (str): Consists of the value `https://w3id.org/xapi/acrossx/verbs/posted`.
        display (dict): Consists of the dictionary `{"en-US": "posted"}`.
    """

    id: VERB_ID_POSTED = VERB_ID_POSTED.__args__[0]
    display: Optional[Dict[LANG_EN_US_DISPLAY, VERB_DISPLAY_POSTED]]
