"""`Activity streams vocabulary` activity types definitions."""

from ...base.unnested_objects import (
    BaseXapiActivityType,
    BaseXapiActivityTypeDefinition,
)
from ..constants.activity_streams_vocabulary import ACTIVITY_PAGE_ID


class PageActivityTypeDefinition(BaseXapiActivityTypeDefinition):
    """Pydantic model for page `Activity` type `definition` property.

    Attributes:
       type (str): Consists of the value `http://activitystrea.ms/schema/1.0/page`.
    """

    type: ACTIVITY_PAGE_ID = ACTIVITY_PAGE_ID.__args__[0]


class PageActivityType(BaseXapiActivityType):
    """Pydantic model for page `Activity` type.

    Attributes:
        definition (dict): See PageActivityTypeDefinition.
    """

    definition: PageActivityTypeDefinition = PageActivityTypeDefinition()
