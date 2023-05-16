"""Tests for the xAPI activity types concepts."""

from ralph.models.xapi.concepts.activity_types.acrossx_profile import (
    MessageActivityType,
)
from ralph.models.xapi.concepts.activity_types.activity_streams_vocabulary import (
    PageActivityType,
)
from ralph.models.xapi.concepts.activity_types.scorm_profile import (
    CMIInteractionActivityType,
)
from ralph.models.xapi.concepts.activity_types.video import VideoActivityType
from ralph.models.xapi.concepts.activity_types.virtual_classroom import (
    VirtualClassroomActivityType,
)

from tests.fixtures.hypothesis_strategies import custom_given

# AcrossX profile


@custom_given(MessageActivityType)
def test_models_xapi_concept_activity_type_message_with_valid_field(field):
    """Tests that a valid message activity type has the expected `definition`.`type`
    property value.
    """
    assert field.definition.type == "https://w3id.org/xapi/acrossx/activities/message"


# Activity Streams Vocabulary


@custom_given(PageActivityType)
def test_models_xapi_concept_activity_type_page_with_valid_field(field):
    """Tests that a valid page activity type has the expected `definition`.`type`
    property value.
    """
    assert field.definition.type == "http://activitystrea.ms/schema/1.0/page"


# Scorm profile


@custom_given(CMIInteractionActivityType)
def test_models_xapi_concept_activity_type_cmi_interaction_with_valid_field(field):
    """Tests that a valid CMI interaction activity type has the expected
    `definition`.`type` property value.
    """
    assert (
        field.definition.type == "http://adlnet.gov/expapi/activities/cmi.interaction"
    )


# Video


@custom_given(VideoActivityType)
def test_models_xapi_concept_activity_type_video_with_valid_field(field):
    """Tests that a valid video activity type has the expected `definition`.`type`
    property value.
    """
    assert field.definition.type == "https://w3id.org/xapi/video/activity-type/video"


# Virtual classroom


@custom_given(VirtualClassroomActivityType)
def test_models_xapi_concept_activity_type_virtual_classroom_with_valid_field(field):
    """Tests that a valid virtual classroom activity type has the expected
    `definition`.`type` property value.
    """
    assert (
        field.definition.type
        == "https://w3id.org/xapi/virtual-classroom/activity-types/virtual-classroom"
    )
