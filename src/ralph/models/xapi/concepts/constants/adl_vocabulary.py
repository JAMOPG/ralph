"""Constants for `ADL Vocabulary` xAPI profile."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# Verb IDs
VERB_ID_ASKED = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/verbs/asked"
]
VERB_ID_ANSWERED = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/verbs/answered"
]

# Verb displays
VERB_DISPLAY_ASKED = Literal["asked"]  # pylint:disable=invalid-name
VERB_DISPLAY_ANSWERED = Literal["answered"]  # pylint:disable=invalid-name
