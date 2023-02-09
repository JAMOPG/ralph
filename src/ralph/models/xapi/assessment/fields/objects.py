"""Video xAPI events object fields definitions."""

from ...fields.unnested_objects import (
    ActivityObjectField,
    InteractionObjectDefinitionField,
    ObjectDefinitionField,
)
from ..constants import ASSESSMENT_OBJECT_DEFINITION_TYPE


class AssessmentObjectDefinitionField(ObjectDefinitionField):
    """Pydantic model for assessment `object`.`definition` field.

    Attributes:
        type (str): Consists of the value
            `http://adlnet.gov/expapi/activities/assessment`.
    """

    type: ASSESSMENT_OBJECT_DEFINITION_TYPE = (
        ASSESSMENT_OBJECT_DEFINITION_TYPE.__args__[0]
    )


class AssessmentObjectField(ActivityObjectField):
    """Pydantic model for assessment `object` field.

    Attributes:
        definition (dict): See AssessmentObjectDefinitionField.
    """

    definition: AssessmentObjectDefinitionField = AssessmentObjectDefinitionField()


class QuestionObjectField(ActivityObjectField):
    """Pydantic model for question `object` field.

    Attributes:
        definition (dict): See InteractionObjectDefinitionField.
    """

    definition: InteractionObjectDefinitionField = InteractionObjectDefinitionField()
