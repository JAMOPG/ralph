"""Constants for `AcrossX Profile` xAPI profile."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# Activity type IRIs
ACTIVITY_TYPE_MESSAGE = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/acrossx/activities/message"
]

# Context extension IDs
CONTEXT_EXTENSION_SCHOOL_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/acrossx/extensions/school"
]

# Verb IDs
VERB_ID_POSTED = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/acrossx/verbs/posted"
]

# Verb displays
VERB_DISPLAY_POSTED = Literal["posted"]  # pylint:disable=invalid-name
