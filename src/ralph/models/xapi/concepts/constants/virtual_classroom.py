"""Constants for `Virtual classroom` xAPI profile."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


VIRTUAL_CLASSROOM_CONTEXT_CATEGORY = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom"
]
VIRTUAL_CLASSROOM_OBJECT_DEFINITION_TYPE = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
]


# Extensions
VIRTUAL_CLASSROOM_CONTEXT_EXTENSIONS_CAMERA_ACTIVATED = (  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/extensions/camera-activated"
)
VIRTUAL_CLASSROOM_CONTEXT_EXTENSIONS_MICRO_ACTIVATED = (  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/extensions/micro-activated"
)
VIRTUAL_CLASSROOM_CONTEXT_EXTENSIONS_SCREEN_SHARED = (  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/extensions/screen-shared"
)
VIRTUAL_CLASSROOM_CONTEXT_EXTENSIONS_HAND_RAISED = (  # pylint:disable=invalid-name
    "https://w3id.org/xapi/virtual-classroom/extensions/hand-raised"
)
