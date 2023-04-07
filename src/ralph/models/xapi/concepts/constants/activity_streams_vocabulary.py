"""Constants for `Activity Streams Vocabulary` xAPI profile."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# Activity types IRIs
ACTIVITY_PAGE_ID = Literal[  # pylint:disable=invalid-name
    "http://activitystrea.ms/schema/1.0/page"
]

# Verb IDs
VERB_ID_JOIN = Literal["http://activitystrea.ms/join"]  # pylint:disable=invalid-name
VERB_ID_LEAVE = Literal["http://activitystrea.ms/leave"]  # pylint:disable=invalid-name

# Verb displays
VERB_DISPLAY_JOINED = Literal["joined"]  # pylint:disable=invalid-name
VERB_DISPLAY_LEFT = Literal["left"]  # pylint:disable=invalid-name
