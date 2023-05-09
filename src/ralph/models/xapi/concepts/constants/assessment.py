"""Constants for `Assessment` xAPI profile."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


ASSESSMENT_CONTEXT_CATEGORY = Literal[  # pylint:disable=invalid-name
    "https://w3id.org/xapi/assessment"
]
