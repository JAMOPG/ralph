"""Constants for `Virtual classroom` xAPI profile."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# Context category
VIRTUAL_CLASSROOM_CONTEXT_CATEGORY = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom"
]

# Object definition type
VIRTUAL_CLASSROOM_ACTIVITY_TYPE = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
]

# Verb IDs
MUTED_VERB_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/verbs/muted"
]
UNMUTED_VERB_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/verbs/unmuted"
]
SHARED_SCREEN_VERB_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/verbs/shared-screen"
]
UNSHARED_SCREEN_VERB_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/verbs/unshared-screen"
]
RAISED_HAND_VERB_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/verbs/raised-hand"
]
LOWERED_HAND_VERB_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/verbs/lowered-hand"
]
STARTED_CAMERA_VERB_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/verbs/started-camera"
]
STOPPED_CAMERA_VERB_ID = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/verbs/stopped-camera"
]

# Verb displays

MUTED_VERB_DISPLAY = Literal["muted"]  # pylint:disable=invalid-name
UNMUTED_VERB_DISPLAY = Literal["unmuted"]  # pylint:disable=invalid-name
SHARED_SCREEN_VERB_DISPLAY = Literal["shared screen"]  # pylint:disable=invalid-name
UNSHARED_SCREEN_VERB_DISPLAY = Literal["unshared screen"]  # pylint:disable=invalid-name
RAISED_HAND_VERB_DISPLAY = Literal["raised hand"]  # pylint:disable=invalid-name
LOWERED_HAND_VERB_DISPLAY = Literal["lowered hand"]  # pylint:disable=invalid-name
STARTED_CAMERA_VERB_DISPLAY = Literal["started camera"]  # pylint:disable=invalid-name
STOPPED_CAMERA_VERB_DISPLAY = Literal["stopped camera"]  # pylint:disable=invalid-name
