"""Constants for `TinCan Vocabulary` xAPI profile."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


# Verb IRIs
VERB_VIEWED_ID = Literal[  # pylint:disable=invalid-name
    "http://id.tincanapi.com/verb/viewed"
]

# Verb displays
VERB_VIEWED_DISPLAY = Literal["viewed"]  # pylint:disable=invalid-name

# Context extension IRIs
CONTEXT_EXTENSION_PLANNED_DURATION = (  # pylint:disable=invalid-name
    "http://id.tincanapi.com/extension/planned-duration"
)
