"""`Virtual classroom` activity types definitions."""

from ...base.unnested_objects import (
    BaseXapiActivityType,
    BaseXapiActivityTypeDefinition,
)
from ..constants.virtual_classroom import VIRTUAL_CLASSROOM_OBJECT_DEFINITION_TYPE


class VirtualClassroomObjectDefinitionField(BaseXapiActivityTypeDefinition):
    """Pydantic model for virtual classroom `object`.`definition` field.

    Attributes:
        type (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom`.
    """

    type: VIRTUAL_CLASSROOM_OBJECT_DEFINITION_TYPE = (
        VIRTUAL_CLASSROOM_OBJECT_DEFINITION_TYPE.__args__[0]
    )


class VirtualClassroomObjectField(BaseXapiActivityType):
    """Pydantic model for virtual classroom `object` field.

    Attributes:
        definition (dict): See VideoObjectDefinitionField.
    """

    definition: VirtualClassroomObjectDefinitionField = (
        VirtualClassroomObjectDefinitionField()
    )
