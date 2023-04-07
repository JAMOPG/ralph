"""`Virtual classroom` activity types definitions."""

from ...fields.unnested_objects import ActivityObjectField, ObjectDefinitionField
from ..constants.virtual_classroom import VIRTUAL_CLASSROOM_OBJECT_DEFINITION_TYPE


class VirtualClassroomObjectDefinitionField(ObjectDefinitionField):
    """Pydantic model for virtual classroom `object`.`definition` field.

    Attributes:
        type (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom`.
    """

    type: VIRTUAL_CLASSROOM_OBJECT_DEFINITION_TYPE = (
        VIRTUAL_CLASSROOM_OBJECT_DEFINITION_TYPE.__args__[0]
    )


class VirtualClassroomObjectField(ActivityObjectField):
    """Pydantic model for virtual classroom `object` field.

    Attributes:
        definition (dict): See VideoObjectDefinitionField.
    """

    definition: VirtualClassroomObjectDefinitionField = (
        VirtualClassroomObjectDefinitionField()
    )
