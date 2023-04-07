"""`Scorm Profile` activity types definitions."""

from ...base.unnested_objects import (
    BaseXapiActivityType,
    BaseXapiActivityTypeDefinition,
)
from ..constants.scorm_profile import ACTIVITY_TYPE_CMI_INTERACTION


# CMI Interaction
class CMIInteractionInteraction(BaseXapiActivityTypeDefinition):
    """Pydantic model for CMI Interaction `Activity` type `definition` property.

    Attributes:
        type (str): Consists of the value
            `http://adlnet.gov/expapi/activities/cmi.interaction`.
    """

    type: ACTIVITY_TYPE_CMI_INTERACTION = ACTIVITY_TYPE_CMI_INTERACTION.__args__[0]


class CMIInteractionActivityType(BaseXapiActivityType):
    """Pydantic model for CMI Interaction `Activity` type.

    Attributes:
        definition (dict): see CMIInteractionInteraction.
    """

    definition: CMIInteractionInteraction = CMIInteractionInteraction()
