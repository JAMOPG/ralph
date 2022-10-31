"""Tests for open response assessment statement event fields"""

import json

import pytest
from pydantic import ValidationError

from ralph.models.edx.open_response_assessment.fields.events import (
    ORAAssessEventField,
    ORAAssessEventRubricField,
    ORACreateSubmissionEventField,
    ORASaveSubmissionEventField,
)

from tests.fixtures.hypothesis_strategies import custom_given


@custom_given(ORAAssessEventField)
def test_models_edx_ora_assess_event_field_with_valid_values(field):
    """Tests that a valid `ORAAssessEventField` does not raise a
    `ValidationError`.
    """

    assert field.score_type in {"PE", "SE", "ST"}


@pytest.mark.parametrize(
    "score_type",
    ["pe", "se", "st", "SA", "PA", "22", "&T"],
)
@custom_given(ORAAssessEventField)
def test_models_edx_ora_assess_event_field_with_invalid_values(score_type, field):
    """Tests that invalid `ORAAssessEventField` raises a `ValidationError`."""

    invalid_field = json.loads(field.json())
    invalid_field["score_type"] = score_type

    with pytest.raises(ValidationError, match="score_type\n  unexpected value"):
        ORAAssessEventField(**invalid_field)


@custom_given(ORACreateSubmissionEventField)
def test_models_edx_ora_create_submission_event_field_with_valid_values(field):
    """Tests that a valid `ORACreateSubmissionEventField` does not raise a
    `ValidationError`.
    """

    assert field.attempt_number == 1


@pytest.mark.parametrize(
    "attempt_number",
    [
        "1",
        27,
        "27",
        "one",
    ],
)
@custom_given(ORACreateSubmissionEventField)
def test_models_edx_ora_create_submission_event_field_with_invalid_values(
    attempt_number, field
):
    """Tests that invalid `ORACreateSubmissionEventField` raises a `ValidationError`."""

    invalid_field = json.loads(field.json())
    invalid_field["attempt_number"] = attempt_number

    with pytest.raises(ValidationError, match="attempt_number\n  unexpected value"):
        ORACreateSubmissionEventField(**invalid_field)


@custom_given(ORASaveSubmissionEventField)
def test_models_edx_ora_save_submission_event_field_with_valid_values(field):
    """Tests that a valid `ORASaveSubmissionEventField` does not raise a
    `ValidationError`.
    """

    if len(field.saved_response.parts) == 0:
        assert [list(part.keys())[0] for part in field.saved_response.parts] == []

    else:
        assert [list(part.keys())[0] for part in field.saved_response.parts] == [
            "text" * len(field.saved_response.parts)
        ]


@pytest.mark.parametrize(
    "fields,error",
    [
        ({}, "saved_response\n  field required"),
        ({"not_saved_response": ""}, "saved_response\n  field required"),
        ({"saved_response": ""}, "Invalid JSON"),
        ({"saved_response": {}}, "saved_response -> parts\n  field required"),
        ({"saved_response": {"parts": ""}}, "parts\n  value is not a valid list"),
        ({"saved_response": {"parts": [None]}}, "none is not an allowed value"),
        (
            {"saved_response": {"parts": [{"not_text": ""}]}},
            "unexpected value; permitted: 'text'",
        ),
        (
            {"saved_response": {"parts": [{"text": None}]}},
            "none is not an allowed value",
        ),
    ],
)
def test_models_edx_ora_save_submission_event_field_with_invalid_values(fields, error):
    """Tests that invalid `ORASaveSubmissionEventField` raises a `ValidationError`."""

    with pytest.raises(ValidationError, match=error):
        ORASaveSubmissionEventField(**fields)


@pytest.mark.parametrize(
    "contenthash",
    [
        "d0d4a647742943e3951b45d9db8a0ea1ff71ae3&",
        "d0d4a647742943e3951b45d9db8a0ea1ff71ae360",
        "D0d4a647742943e3951b45d9db8a0ea1ff71ae36",
    ],
)
@custom_given(ORAAssessEventRubricField)
def test_models_edx_ora_assess_event_rubric_field_with_invalid_problem_id_value(
    contenthash, field
):
    """Tests that an invalid `problem_id` value in `ProblemCheckEventField` raises a
    `ValidationError`.
    """

    invalid_field = json.loads(field.json())
    invalid_field["contenthash"] = contenthash

    with pytest.raises(
        ValidationError, match="contenthash\n  string does not match regex"
    ):
        ORAAssessEventRubricField(**invalid_field)
