"""`Assessment` xAPI event definitions."""

from datetime import datetime

from ...selector import selector
from ..base.statements import BaseXapiStatement
from ..concepts.activity_types.scorm_profile import CMIInteractionActivityType
from ..concepts.verbs.scorm_profile import (
    CompletedVerb,
    InitializedVerb,
    LaunchedVerb,
    TerminatedVerb,
)
from .contexts import AssessmentContext

# Mandatory statements


class AssessmentInitialized(BaseXapiStatement):
    """Pydantic model for assessment initialized statement.

    Example:

    Attributes:
        verb (dict): See InitializedVerb.
        object (dict): See CMIInteractionActivityType.
        context (dict): See AssessmentContext.
        timestamp (datetime): Consists of the timestamp of when the event occurred.
    """

    __selector__ = selector(
        verb__id="http://adlnet.gov/expapi/verbs/initialized",
        object__definition__type=(
            "http://adlnet.gov/expapi/activities/cmi.interaction"
        ),
    )

    verb: InitializedVerb = InitializedVerb()
    object: CMIInteractionActivityType
    context: AssessmentContext
    timestamp: datetime


class AssessmentLaunched(BaseXapiStatement):
    """Pydantic model for assessment launched statement.

    Example:

    Attributes:
        verb (dict): See LaunchedVerb.
        object (dict): See CMIInteractionActivityType.
        context (dict): See AssessmentContext.
        timestamp (datetime): Consists of the timestamp of when the event occurred.
    """

    __selector__ = selector(
        verb__id="http://adlnet.gov/expapi/verbs/launched",
        object__definition__type=(
            "http://adlnet.gov/expapi/activities/cmi.interaction"
        ),
    )

    verb: LaunchedVerb = LaunchedVerb()
    object: CMIInteractionActivityType
    context: AssessmentContext
    timestamp: datetime


class AssessmentCompleted(BaseXapiStatement):
    """Pydantic model for assessment completed statement.

    Example:

    Attributes:
        verb (dict): See CompletedVerb.
        result (dict): See CMIInteractionActivityType.
        context (dict): See VideoCompletedContext.
    """

    __selector__ = selector(
        object__definition__type="http://adlnet.gov/expapi/activities/cmi.interaction",
        verb__id="http://adlnet.gov/expapi/verbs/completed",
    )

    verb: CompletedVerb = CompletedVerb()
    result: CMIInteractionActivityType
    context: AssessmentContext
    timestamp: datetime


class AssessmentTerminated(BaseXapiStatement):
    """Pydantic model for assessment terminated statement.

    Example:

    Attributes:
        verb (dict): See CompletedVerb.
        result (dict): See CMIInteractionActivityType.
        context (dict): See VideoCompletedContext.
    """

    __selector__ = selector(
        object__definition__type="http://adlnet.gov/expapi/activities/cmi.interaction",
        verb__id="http://adlnet.gov/expapi/verbs/terminated",
    )

    verb: TerminatedVerb = TerminatedVerb()
    result: CMIInteractionActivityType
    context: AssessmentContext
    timestamp: datetime
