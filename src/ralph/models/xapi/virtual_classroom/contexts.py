"""Virtual classroom xAPI events context fields definitions."""

from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from pydantic import Field

from ..base.contexts import BaseXapiContext, BaseXapiContextContextActivities
from ..base.unnested_objects import BaseXapiActivityType, BaseXapiActivityTypeDefinition
from ..concepts.activity_types.virtual_classroom import VirtualClassroomActivityType
from ..concepts.constants.cmi5_profile import CONTEXT_EXTENSION_SESSION_ID
from ..concepts.constants.tincan_vocabulary import CONTEXT_EXTENSION_PLANNED_DURATION
from ..concepts.constants.virtual_classroom import VIRTUAL_CLASSROOM_CONTEXT_CATEGORY
from ..config import BaseExtensionModelWithConfig
from ..constants import CONTEXT_CONTEXTACTIVTIES_CATEGORY_DEFINITION_TYPE


class VirtualClassroomContextActivitiesCategoryDefinition(
    BaseXapiActivityTypeDefinition
):
    # noqa: D205
    """Pydantic model for virtual classroom `context`.`contextActivities`.`category`.
    `definition` property.

    Attributes:
        type (str): Consists of the value `http://adlnet.gov/expapi/activities/profile`.
    """

    type: CONTEXT_CONTEXTACTIVTIES_CATEGORY_DEFINITION_TYPE = (
        CONTEXT_CONTEXTACTIVTIES_CATEGORY_DEFINITION_TYPE.__args__[0]
    )


class VirtualClassroomContextActivitiesCategory(BaseXapiActivityType):
    # noqa: D205, D415
    """Pydantic model for virtual classroom `context`.`contextActivities`.`category`
    property.

    Attributes:
        id (str): Consists of the value `https://w3id.org/xapi/virtual-classroom`.
        definition (dict): see VirtualClassroomContextActivitiesCategoryDefinition.
    """

    id: VIRTUAL_CLASSROOM_CONTEXT_CATEGORY = (
        VIRTUAL_CLASSROOM_CONTEXT_CATEGORY.__args__[0]
    )
    definition: VirtualClassroomContextActivitiesCategoryDefinition = (
        VirtualClassroomContextActivitiesCategoryDefinition()
    )


class VirtualClassroomContextActivities(BaseXapiContextContextActivities):
    """Pydantic model for virtual classroom `context`.`contextActivities` property.

    Attributes:
        category (list): see VirtualClassroomContextActivitiesCategory.
    """

    category: Union[
        VirtualClassroomContextActivitiesCategory,
        List[VirtualClassroomContextActivitiesCategory],
    ]


class VirtualClassroomContextExtensions(BaseExtensionModelWithConfig):
    """Pydantic model for virtual classroom base `context`.`extensions` property.

    Attributes:
        session_id (str): Consists of the ID of the active session.
    """

    session_id: str = Field(alias=CONTEXT_EXTENSION_SESSION_ID, default="")


class VirtualClassroomContext(BaseXapiContext):
    """Pydantic model for virtual classroom base `context` property.

    Attributes:
        registration (uuid): the registration that the Statement is associated with.
        extensions (dict): see VirtualClassroomExtensions.
    """

    contextActivities: VirtualClassroomContextActivities
    registration: UUID
    extensions: VirtualClassroomContextExtensions


# Initialized statement


class VirtualClassroomInitializedContextExtensions(VirtualClassroomContextExtensions):
    """Pydantic model for virtual classroom initialized `context`.`extensions` property.

    Attributes:
        planned_duration (datetime): Consists of the estimated duration of the scheduled
            virtual classroom.
    """

    planned_duration: Optional[datetime] = Field(
        alias=CONTEXT_EXTENSION_PLANNED_DURATION
    )


class VirtualClassroomInitializedContext(VirtualClassroomContext):
    """Pydantic model for virtual classroom initialized `context` property.

    Attributes:
        extensions (dict): see VirtualClassroomInitializedContextExtensions.
    """

    extensions: VirtualClassroomInitializedContextExtensions


# Joined statement


class VirtualClassroomJoinedContextExtensions(VirtualClassroomContextExtensions):
    """Pydantic model for virtual classroom initialized `context`.`extensions` property.

    Attributes:
        planned_duration (datetime): Consists of the estimated duration of the scheduled
            virtual classroom.
    """

    planned_duration: Optional[datetime] = Field(
        alias=CONTEXT_EXTENSION_PLANNED_DURATION
    )


class VirtualClassroomJoinedContext(VirtualClassroomContext):
    """Pydantic model for virtual classroom joined `context` property.

    Attributes:
        extensions (dict): see VirtualClassroomJoinedContextExtensions.
    """

    extensions: VirtualClassroomJoinedContextExtensions


# Terminated statement


class VirtualClassroomTerminatedContextExtensions(VirtualClassroomContextExtensions):
    """Pydantic model for virtual classroom terminated `context`.`extensions` property.

    Attributes:
        planned_duration (datetime): Consists of the estimated duration of the scheduled
            virtual classroom.
    """

    planned_duration: Optional[datetime] = Field(
        alias=CONTEXT_EXTENSION_PLANNED_DURATION
    )


class VirtualClassroomTerminatedContext(VirtualClassroomContext):
    """Pydantic model for virtual classroom terminated `context` property.

    Attributes:
        extensions (dict): see VirtualClassroomInitializedContextExtensions.
    """

    extensions: VirtualClassroomTerminatedContextExtensions


class VirtualClassroomStartedPollContextActivities(VirtualClassroomContextActivities):
    # noqa: D205, D415
    """Pydantic model for virtual classroom started poll `context`.`contextActivities`
    property.

    Attributes:
        parent (list): see VirtualClassroomActivityType.
    """

    parent: Union[VirtualClassroomActivityType, List[VirtualClassroomActivityType]]


class VirtualClassroomStartedPollContext(VirtualClassroomContext):
    """Pydantic model for virtual classroom started poll `context` property.

    Attributes:
        extensions (dict): see VirtualClassroomContextExtensions.
        contextActivities (dict): see
            VirtualClassroomStartedPollContextActivities.
    """

    extensions: VirtualClassroomContextExtensions
    contextActivities: VirtualClassroomStartedPollContextActivities


# Answered poll statement


class VirtualClassroomAnsweredPollContextActivities(VirtualClassroomContextActivities):
    # noqa: D205, D415
    """Pydantic model for virtual classroom answered poll `context`.`contextActivities`
    property.

    Attributes:
        parent (list): see VirtualClassroomActivityType.
    """

    parent: Union[VirtualClassroomActivityType, List[VirtualClassroomActivityType]]


class VirtualClassroomAnsweredPollContext(VirtualClassroomContext):
    """Pydantic model for virtual classroom answered poll `context` property.

    Attributes:
        extensions (dict): see VirtualClassroomContextExtensions.
        contextActivites (dict): see VirtualClassroomAnsweredPollContextActivities.
    """

    extensions: VirtualClassroomContextExtensions
    contextActivities: VirtualClassroomAnsweredPollContextActivities


# Posted public message statement


class VirtualClassroomPostedPublicMessageContextActivities(
    VirtualClassroomContextActivities
):
    # noqa: D205, D415
    """Pydantic model for virtual classroom posted public message
    `context`.`contextActivities` property.

    Attributes:
        parent (list): see VirtualClassroomActivityType.
    """

    parent: Union[VirtualClassroomActivityType, List[VirtualClassroomActivityType]]


class VirtualClassroomPostedPublicMessageContext(VirtualClassroomContext):
    """Pydantic model for virtual classroom posted public message `context` property.

    Attributes:
        extensions (dict): see VirtualClassroomContextExtensions.
        contextActivities (list): see
            VirtualClassroomPostedPublicMessageContextActivities.
    """

    extensions: VirtualClassroomContextExtensions
    contextActivities: VirtualClassroomPostedPublicMessageContextActivities
