"""`Assessment` xAPI events context fields definitions."""

from typing import List, Union

from ..base.contexts import BaseXapiContext, BaseXapiContextContextActivities
from ..base.unnested_objects import BaseXapiActivityType, BaseXapiActivityTypeDefinition
from ..concepts.constants.assessment import ASSESSMENT_CONTEXT_CATEGORY
from ..constants import CONTEXT_CONTEXTACTIVTIES_CATEGORY_DEFINITION_TYPE


class AssessmentContextActivitiesCategoryDefinition(BaseXapiActivityTypeDefinition):
    # noqa: D205
    """Pydantic model for assessment `context`.`contextActivities`.`category`.
    `definition` property.

    Attributes:
        type (str): Consists of the value `http://adlnet.gov/expapi/activities/profile`.
    """

    type: CONTEXT_CONTEXTACTIVTIES_CATEGORY_DEFINITION_TYPE = (
        CONTEXT_CONTEXTACTIVTIES_CATEGORY_DEFINITION_TYPE.__args__[0]
    )


class AssessmentContextActivitiesCategory(BaseXapiActivityType):
    # noqa: D205, D415
    """Pydantic model for assessment `context`.`contextActivities`.`category`
    property.

    Attributes:
        id (str): Consists of the value `https://w3id.org/xapi/virtual-classroom`.
        definition (dict): see AssessmentContextActivitiesCategoryDefinition.
    """

    id: ASSESSMENT_CONTEXT_CATEGORY = ASSESSMENT_CONTEXT_CATEGORY.__args__[0]
    definition: AssessmentContextActivitiesCategoryDefinition = (
        AssessmentContextActivitiesCategoryDefinition()
    )


class AssessmentContextActivities(BaseXapiContextContextActivities):
    """Pydantic model for assessment `context`.`contextActivities` property.

    Attributes:
        category (list): see AssessmentContextActivitiesCategory.
    """

    category: Union[
        AssessmentContextActivitiesCategory,
        List[AssessmentContextActivitiesCategory],
    ] = [AssessmentContextActivitiesCategory()]


class AssessmentContext(BaseXapiContext):
    """Pydantic model for assessment base `context` property.

    Attributes:
        contextActivities: see AssessmentContextActivities.
    """

    contextActivities: AssessmentContextActivities = AssessmentContextActivities()
