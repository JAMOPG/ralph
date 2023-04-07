"""Tests for the base xAPI `Object` definitions."""

import json
import re

import pytest
from pydantic import ValidationError

from ralph.models.xapi.base.unnested_objects import (
    BaseXapiActivityTypeInteractionDefinition,
    BaseXapiInteractionComponent,
    BaseXapiStatementRefType,
)

from tests.fixtures.hypothesis_strategies import custom_given


@custom_given(BaseXapiStatementRefType)
def test_models_xapi_base_object_statement_ref_type_with_valid_field(field):
    """Tests a valid BaseXapiStatementRefType has the expected `objectType` value."""

    assert field.objectType == "StatementRef"


@custom_given(BaseXapiInteractionComponent)
def test_models_xapi_base_object_interaction_component_with_valid_field(
    field,
):
    """Tests a valid BaseXapiInteractionComponent has the expected `id` regex."""

    assert re.match(r"^[^\s]+$", field.id)


@pytest.mark.parametrize(
    "id_value",
    [" test_id", "\ntest"],
)
@custom_given(BaseXapiInteractionComponent)
def test_models_xapi_base_object_interaction_component_with_invalid_field(
    id_value, field
):
    """Tests a invalid `id` property in
    BaseXapiInteractionComponent raises a `ValidationError`.
    """

    invalid_property = json.loads(field.json())
    invalid_property["id"] = id_value

    with pytest.raises(ValidationError, match="id\n  string does not match regex"):
        BaseXapiInteractionComponent(**invalid_property)


@custom_given(BaseXapiActivityTypeInteractionDefinition)
def test_models_xapi_base_object_activity_type_interaction_definition_with_valid_field(
    field,
):
    """Tests a valid BaseXapiActivityTypeInteractionDefinition has the expected
    `objectType` value.
    """

    assert field.interactionType in (
        "true-false",
        "choice",
        "fill-in",
        "long-fill-in",
        "matching",
        "performance",
        "sequencing",
        "likert",
        "numeric",
        "other",
    )
