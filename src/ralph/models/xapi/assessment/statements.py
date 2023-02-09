"""Video xAPI event definitions."""

from typing import Optional

from ...selector import selector
from ..base import BaseXapiModel
from ..fields.results import ResultField
from .fields.contexts import AssessmentContextField
from .fields.objects import QuestionObjectField
from .fields.verbs import AnsweredVerbField


class AssessmentAnsweredQuestion(BaseXapiModel):
    """Pydantic model for video answered question statement.

    Example: John has answered a question in an assessment.

    Attributes:
        object (dict): See QuestionObjectField.
        verb (dict): See AnsweredVerbField.
        context (dict): See AssessmentContextField.
    """

    __selector__ = selector(
        verb__id="http://adlnet.gov/expapi/verbs/answered",
        context__contextActivities__definition__type=(
            "http://adlnet.gov/expapi/activities/assessment"
        ),
    )

    object: QuestionObjectField = QuestionObjectField()
    verb: AnsweredVerbField = AnsweredVerbField()
    context: AssessmentContextField = AssessmentContextField()
    result: Optional[ResultField]
