"""Constants for xAPI assessment specifications."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# xAPI assessment object definition type
ASSESSMENT_OBJECT_DEFINITION_TYPE = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/activities/assessment"
]

# xAPI question object definition type
QUESTION_OBJECT_DEFINITION_TYPE = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/activities/question"
]

# Assessment context category
ASSESSMENT_CONTEXT_CATEGORY = Literal[  # pylint:disable=invalid-name
    "http://schema.dases.eu/xapi/profile/assessment"
]
