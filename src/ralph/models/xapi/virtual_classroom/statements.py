"""Virtual classroom xAPI event definitions."""

from datetime import datetime

from ...selector import selector
from ..base.statements import BaseXapiStatement
from ..concepts.activity_types.acrossx_profile import MessageActivityType
from ..concepts.activity_types.scorm_profile import CMIInteractionActivityType
from ..concepts.activity_types.virtual_classroom import VirtualClassroomActivityType
from ..concepts.verbs.acrossx_profile import PostedVerb
from ..concepts.verbs.activity_streams_vocabulary import JoinVerb, LeaveVerb
from ..concepts.verbs.adl_vocabulary import AnsweredVerb, AskedVerb
from ..concepts.verbs.scorm_profile import InitializedVerb, TerminatedVerb
from ..concepts.verbs.virtual_classroom import (
    LoweredHandVerb,
    MutedVerb,
    RaisedHandVerb,
    SharedScreenVerb,
    StartedCameraVerb,
    StoppedCameraVerb,
    UnmutedVerb,
    UnsharedScreenVerb,
)
from .contexts import (
    VirtualClassroomAnsweredPollContext,
    VirtualClassroomContext,
    VirtualClassroomInitializedContext,
    VirtualClassroomJoinedContext,
    VirtualClassroomPostedPublicMessageContext,
    VirtualClassroomStartedPollContext,
    VirtualClassroomTerminatedContext,
)
from .results import VirtualClassroomAnsweredPollResult


class BaseVirtualClassroomStatement(BaseXapiStatement):
    """Pydantic model for Virtual Classroom core statements.

    Attributes:
        timestamp (datetime): Consists of the timestamp of when the event occurred.
    """

    timestamp: datetime


# Mandatory statements


class VirtualClassroomInitialized(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom initialized statement.

    Example: John has entered the virtual classroom as the first user.

    Attributes:
        verb (dict): See InitializedVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomInitializedContext.
    """

    __selector__ = selector(
        verb__id="http://adlnet.gov/expapi/verbs/initialized",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: InitializedVerb = InitializedVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomInitializedContext


class VirtualClassroomJoined(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom joined statement.

    Example: Jane has entered the virtual classroom.

    Attributes:
        verb (dict): See JoinVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomJoinedContext.
    """

    __selector__ = selector(
        verb__id="http://activitystrea.ms/join",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: JoinVerb = JoinVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomJoinedContext


class VirtualClassroomLeft(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom joined statement.

    Example: Jane has left the virtual classroom.

    Attributes:
        verb (dict): See LeaveVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomContext.

    """

    __selector__ = selector(
        verb__id="http://activitystrea.ms/leave",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: LeaveVerb = LeaveVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomTerminated(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom terminated statement.

    Example: Jane has terminated the virtual classroom.

    Attributes:
        verb (dict): See TerminatedVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomTerminatedContext.

    """

    __selector__ = selector(
        verb__id="http://adlnet.gov/expapi/verbs/terminated",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: TerminatedVerb = TerminatedVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomTerminatedContext


# Recommended statements


class VirtualClassroomMuted(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom muted statement.

    Example: Jane has muted herself or has been muted.

    Attributes:
        verb (dict): See MutedVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomMutedContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/virtual-classroom/verbs/muted",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: MutedVerb = MutedVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomUnmuted(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom unmuted statement.

    Example: Jane has unmuted herself or has been unmuted.

    Attributes:
        verb (dict): See UnmutedVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/virtual-classroom/verbs/unmuted",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: UnmutedVerb = UnmutedVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomStartedCamera(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom started camera statement.

    Example: Jane has started her camera.

    Attributes:
        verb (dict): See StartedCameraVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/virtual-classroom/verbs/started-camera",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: StartedCameraVerb = StartedCameraVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomStoppedCamera(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom stopped camera statement.

    Example: Jane has stopped her camera.

    Attributes:
        verb (dict): See StoppedCameraVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomStoppedCameraContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/virtual-classroom/verbs/stopped-camera",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: StoppedCameraVerb = StoppedCameraVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomSharedScreen(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom shared screen statement.

    Example: Jane has shared her screen.

    Attributes:
        verb (dict): See SharedScreenVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomSharedScreenContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/virtual-classroom/verbs/shared-screen",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: SharedScreenVerb = SharedScreenVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomUnsharedScreen(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom unshared screen statement.

    Example: Jane has unshared her screen or her screen has been unshared by the
    moderator.

    Attributes:
        verb (dict): See UnsharedScreenVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomUnsharedScreenContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/virtual-classroom/verbs/unshared-screen",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: UnsharedScreenVerb = UnsharedScreenVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomRaisedHand(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom raised hand statement.

    Example: Jane has raised the hand.

    Attributes:
        verb (dict): See RaisedHandVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomRaisedHandContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/virtual-classroom/verbs/raised-hand",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: RaisedHandVerb = RaisedHandVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomLoweredHand(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom lowered hand statement.

    Example: Jane has lowered the hand.

    Attributes:
        verb (dict): See LoweredHandVerb.
        object (dict): See VirtualClassroomActivityType.
        context (dict): See VirtualClassroomLoweredHandContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/virtual-classroom/verbs/lowered-hand",
        object__definition__type=(
            "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
        ),
    )

    verb: LoweredHandVerb = LoweredHandVerb()
    object: VirtualClassroomActivityType
    context: VirtualClassroomContext


class VirtualClassroomStartedPoll(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom started poll statement.

    Example: A poll has been started in the virtual classroom in order
    to collect participants opinions about a given question.

    Attributes:
        verb (dict): See AskedVerb.
        object (dict): See CMIInteractionActivityType.
        context (dict): See VirtualClassroomLoweredHandContext.

    """

    __selector__ = selector(
        verb__id="http://adlnet.gov/expapi/verbs/asked",
        object__definition__type=(
            "http://adlnet.gov/expapi/activities/cmi.interaction"
        ),
    )

    verb: AskedVerb = AskedVerb()
    object: CMIInteractionActivityType
    context: VirtualClassroomStartedPollContext


class VirtualClassroomAnsweredPoll(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom answered poll statement.

    Example: John answered to a poll question.

    Attributes:
        verb (dict): See AskedVerb.
        object (dict): See CMIInteractionActivityType.
        context (dict): See VirtualClassroomAnsweredPollContext.
        result (dict): See AnsweredPollResult.
        result (dict): See AnsweredPollResult.
        timestamp (datetime): Consists of the timestamp of when the event occurred.
        result (dict): See AnsweredPollResult.
        timestamp (datetime): Consists of the timestamp of when the event occurred.
    """

    __selector__ = selector(
        verb__id="http://adlnet.gov/expapi/verbs/answered",
        object__definition__type=(
            "http://adlnet.gov/expapi/activities/cmi.interaction"
        ),
    )

    verb: AnsweredVerb = AnsweredVerb()
    object: CMIInteractionActivityType
    context: VirtualClassroomAnsweredPollContext
    result: VirtualClassroomAnsweredPollResult


class VirtualClassroomPostedPublicMessage(BaseVirtualClassroomStatement):
    """Pydantic model for virtual classroom posted public message statement.

    Example: John sent a message in the public chat.

    Attributes:
        verb (dict): See PostedVerb.
        object (dict): See MessageActivityType.
        context (dict): See VirtualClassroomPostedPublicMessageContext.

    """

    __selector__ = selector(
        verb__id="https://w3id.org/xapi/acrossx/verbs/posted",
        object__definition__type="https://w3id.org/xapi/acrossx/activities/message",
    )

    verb: PostedVerb = PostedVerb()
    object: MessageActivityType
    context: VirtualClassroomPostedPublicMessageContext
