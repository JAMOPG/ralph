"""`AcrossX Profile` activity types definitions."""

from ...base.unnested_objects import (
    BaseXapiActivityType,
    BaseXapiActivityTypeDefinition,
)
from ..constants.acrossx_profile import ACTIVITY_TYPE_MESSAGE


# Message
class MessageActivityTypeDefinition(BaseXapiActivityTypeDefinition):
    """Pydantic model for message `Activity` type `definition` property.

    Attributes:
        type (str): Consists of the value
            `https://w3id.org/xapi/acrossx/activities/message`.
    """

    type: ACTIVITY_TYPE_MESSAGE = ACTIVITY_TYPE_MESSAGE.__args__[0]


class MessageActivityType(BaseXapiActivityType):
    """Pydantic model for message `Activity` type.

    Attributes:
        definition (dict): see MessageActivityTypeDefinition.
    """

    definition: MessageActivityTypeDefinition = MessageActivityTypeDefinition()
