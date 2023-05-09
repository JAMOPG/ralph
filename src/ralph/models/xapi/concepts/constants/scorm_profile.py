"""Constants for `Scorm Profile` xAPI profile."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# Verb IDs
VERB_COMPLETED_ID = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/verbs/completed"
]
VERB_INITIALIZED_ID = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/verbs/initialized"
]
VERB_INTERACTED_ID = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/verbs/interacted"
]
VERB_LAUNCHED_ID = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/verbs/launched"
]
VERB_TERMINATED_ID = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/verbs/terminated"
]

# Verb displays
VERB_COMPLETED_DISPLAY = Literal["completed"]  # pylint:disable=invalid-name
VERB_INITIALIZED_DISPLAY = Literal["initialized"]  # pylint:disable=invalid-name
VERB_INTERACTED_DISPLAY = Literal["interacted"]  # pylint:disable=invalid-name
VERB_LAUNCHED_DISPLAY = Literal["launched"]  # pylint:disable=invalid-name
VERB_TERMINATED_DISPLAY = Literal["terminated"]  # pylint:disable=invalid-name

# Activity types IRIs
ACTIVITY_TYPE_COURSE = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/activities/course"
]
ACTIVITY_TYPE_MODULE = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/activities/module"
]
ACTIVITY_TYPE_CMI_INTERACTION = Literal[  # pylint:disable=invalid-name
    "http://adlnet.gov/expapi/activities/cmi.interaction"
]
