"""Assessment xAPI events context fields definitions."""

from typing import Dict, List, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from ...config import BaseModelWithConfig
from ...fields.contexts import ContextActivitiesContextField
from ..constants import ASSESSMENT_CONTEXT_CATEGORY
from .objects import AssessmentObjectField


class AssessmentContextActivitiesField(ContextActivitiesContextField):
    """Pydantic model for assessment `context`.`contextActivities` field.

    Attributes:
        category (List): Consists of a list containing the dictionary
            {"id": "http://schema.dases.eu/xapi/profile/assessment"}.
        parent (List): See AssessmentObjectField.
    """

    category: Union[
        Dict[Literal["id"], ASSESSMENT_CONTEXT_CATEGORY],
        List[Dict[Literal["id"], ASSESSMENT_CONTEXT_CATEGORY]],
    ] = [{"id": ASSESSMENT_CONTEXT_CATEGORY.__args__[0]}]
    parent: Union[AssessmentObjectField, List[AssessmentObjectField]] = [
        AssessmentObjectField()
    ]


class AssessmentContextField(BaseModelWithConfig):
    """Pydantic model for assessment `context` field.

    Attributes:
        contextActivities (json): see AssessmentContextActivitiesField.
    """

    contextActivities: AssessmentContextActivitiesField = (
        AssessmentContextActivitiesField()
    )
