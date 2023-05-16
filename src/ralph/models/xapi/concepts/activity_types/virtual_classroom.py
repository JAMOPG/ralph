"""`Virtual classroom` activity types definitions."""

from ...base.unnested_objects import (
    BaseXapiActivityType,
    BaseXapiActivityTypeDefinition,
)
from ..constants.virtual_classroom import VIRTUAL_CLASSROOM_ACTIVITY_TYPE

# Virtual classroom


class VirtualClassroomActivityTypeDefinition(BaseXapiActivityTypeDefinition):
    """Pydantic model for virtual classroom `Activity` type `definition` property.

    Attributes:
        type (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom`.
    """

    type: VIRTUAL_CLASSROOM_ACTIVITY_TYPE = VIRTUAL_CLASSROOM_ACTIVITY_TYPE.__args__[0]


class VirtualClassroomActivityType(BaseXapiActivityType):
    """Pydantic model for virtual classroom `Activity` type.

    Attributes:
        definition (dict): See VirtualClassroomActivityTypeDefinition.
    """

    definition: VirtualClassroomActivityTypeDefinition = (
        VirtualClassroomActivityTypeDefinition()
    )
