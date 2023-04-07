"""Tests for the xAPI verbs concepts."""
from ralph.models.xapi.concepts.verbs.acrossx_profile import PostedVerb
from ralph.models.xapi.concepts.verbs.activity_streams_vocabulary import (
    JoinVerb,
    LeaveVerb,
)
from ralph.models.xapi.concepts.verbs.adl_vocabulary import AnsweredVerb, AskedVerb
from ralph.models.xapi.concepts.verbs.scorm_profile import (
    CompletedVerb,
    InitializedVerb,
    InteractedVerb,
    TerminatedVerb,
)
from ralph.models.xapi.concepts.verbs.tincan_vocabulary import ViewedVerb
from ralph.models.xapi.concepts.verbs.video import PausedVerb, PlayedVerb, SeekedVerb

from tests.fixtures.hypothesis_strategies import custom_given

# AcrossX Profile


@custom_given(PostedVerb)
def test_models_xapi_concept_verb_posted_with_valid_field(field):
    """Tests that a valid posted verb has the expected `id` property value."""
    assert field.id == "https://w3id.org/xapi/acrossx/verbs/posted"


# Activity streams vocabulary


@custom_given(JoinVerb)
def test_models_xapi_concept_verb_join_with_valid_field(field):
    """Tests that a valid join verb has the expected `id` property value."""
    assert field.id == "http://activitystrea.ms/join"


@custom_given(LeaveVerb)
def test_models_xapi_concept_verb_leave_with_valid_field(field):
    """Tests that a valid leave verb has the expected `id` property value."""
    assert field.id == "http://activitystrea.ms/leave"


# ADL Vocabulary


@custom_given(AnsweredVerb)
def test_models_xapi_concept_verb_answered_with_valid_field(field):
    """Tests that a valid answered verb has the expected `id` property value."""
    assert field.id == "http://adlnet.gov/expapi/verbs/answered"


@custom_given(AskedVerb)
def test_models_xapi_concept_verb_asked_with_valid_field(field):
    """Tests that a valid asked verb has the expected `id` property value."""
    assert field.id == "http://adlnet.gov/expapi/verbs/asked"


# Scorm profile


@custom_given(CompletedVerb)
def test_models_xapi_concept_verb_completed_with_valid_field(field):
    """Tests that a valid completed verb has the expected `id` property value."""
    assert field.id == "http://adlnet.gov/expapi/verbs/completed"


@custom_given(InitializedVerb)
def test_models_xapi_concept_verb_initialized_with_valid_field(field):
    """Tests that a valid initialized verb has the expected `id` property value."""
    assert field.id == "http://adlnet.gov/expapi/verbs/initialized"


@custom_given(InteractedVerb)
def test_models_xapi_concept_verb_interacted_with_valid_field(field):
    """Tests that a valid interacted verb has the expected `id` property value."""
    assert field.id == "http://adlnet.gov/expapi/verbs/interacted"


@custom_given(TerminatedVerb)
def test_models_xapi_concept_verb_terminated_with_valid_field(field):
    """Tests that a valid terminated verb has the expected `id` property value."""
    assert field.id == "http://adlnet.gov/expapi/verbs/terminated"


# TinCan Vocabulary


@custom_given(ViewedVerb)
def test_models_xapi_concept_verb_viewed_with_valid_field(field):
    """Tests that a valid viewed verb has the expected `id` property value."""
    assert field.id == "http://id.tincanapi.com/verb/viewed"


# Video


@custom_given(PlayedVerb)
def test_models_xapi_concept_verb_played_with_valid_field(field):
    """Tests that a valid played verb has the expected `id` property value."""
    assert field.id == "https://w3id.org/xapi/video/verbs/played"


@custom_given(PausedVerb)
def test_models_xapi_concept_verb_paused_with_valid_field(field):
    """Tests that a valid paused verb has the expected `id` property value."""
    assert field.id == "https://w3id.org/xapi/video/verbs/paused"


@custom_given(SeekedVerb)
def test_models_xapi_concept_verb_seeked_with_valid_field(field):
    """Tests that a valid seeked verb has the expected `id` property value."""
    assert field.id == "https://w3id.org/xapi/video/verbs/seeked"
