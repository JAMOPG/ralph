"""Base xAPI `Context` definitions."""

from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import StrictStr

from ..config import BaseModelWithConfig
from .actors import BaseXapiActor, BaseXapiGroupType
from .common import IRI, LanguageTag
from .unnested_objects import BaseXapiActivityType, BaseXapiStatementRefType


class BaseXapiContextContextActivities(BaseModelWithConfig):
    """Pydantic model for context `contextActivities` property.

    Attributes:
        parent (List): An Activity with a direct relation to the statement's Activity.
        grouping (List): An Activity with an indirect relation to the statement's
            Activity.
        category (List): An Activity used to categorize the Statement.
        other (List): A contextActivity that doesn't fit one of the other properties.
    """

    parent: Optional[Union[BaseXapiActivityType, List[BaseXapiActivityType]]]
    grouping: Optional[Union[BaseXapiActivityType, List[BaseXapiActivityType]]]
    category: Optional[Union[BaseXapiActivityType, List[BaseXapiActivityType]]]
    other: Optional[Union[BaseXapiActivityType, List[BaseXapiActivityType]]]


class BaseXapiContext(BaseModelWithConfig):
    """Pydantic model for `context` property.

    Attributes:
        registration (UUID): The registration that the Statement is associated with.
        instructor (ActorField): The instructor that the Statement relates to.
        team (GroupActorField): The team that this Statement relates to.
        contextActivities (dict): See ContextActivitiesContextField.
        revision (str): The revision of the activity associated with this Statement.
        platform (str): The platform where the learning activity took place.
        language (LanguageTag): The language in which the experience occurred.
        statement (StatementRef): Another Statement giving context for this Statement.
        extensions (dict): Consists of an dictionary of other properties as needed.
    """

    registration: Optional[UUID]
    instructor: Optional[BaseXapiActor]
    team: Optional[BaseXapiGroupType]
    contextActivities: Optional[BaseXapiContextContextActivities]
    revision: Optional[StrictStr]
    platform: Optional[StrictStr]
    language: Optional[LanguageTag]
    statement: Optional[BaseXapiStatementRefType]
    extensions: Optional[Dict[IRI, Union[str, int, bool, list, dict, None]]]
