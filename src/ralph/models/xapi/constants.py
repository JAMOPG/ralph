"""Constants for xAPI specifications."""

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

# Languages
LANG_EN_US_DISPLAY = Literal["en-US"]  # pylint:disable=invalid-name

# xAPI extensions
EXTENSION_COURSE_ID = "http://adlnet.gov/expapi/activities/course"
EXTENSION_MODULE_ID = "http://adlnet.gov/expapi/activities/module"
EXTENSION_SCHOOL_ID = "https://w3id.org/xapi/acrossx/extensions/school"


# xAPI profile constants

CONTEXT_CONTEXTACTIVTIES_CATEGORY_DEFINITION_TYPE = (  # pylint:disable=invalid-name
    Literal["http://adlnet.gov/expapi/activities/profile"]
)
