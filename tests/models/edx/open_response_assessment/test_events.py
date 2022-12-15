"""Tests for open response assessment statement event fields."""

import json
import re

import pytest
from pydantic import ValidationError

from ralph.models.edx.open_response_assessment.fields.events import (
    ORAAssessEventField,
    ORAAssessEventRubricField,
    ORACreateSubmissionEventField,
    ORAGetPeerSubmissionEventField,
    ORAGetSubmissionForStaffGradingEventField,
    ORASaveSubmissionEventField,
)

from tests.fixtures.hypothesis_strategies import custom_given


@custom_given(ORAGetPeerSubmissionEventField)
def test_models_edx_ora_get_peer_submission_event_field_with_valid_values(field):
    """Tests that a valid `ORAGetPeerSubmissionEventField` does not raise a
    `ValidationError`."""

    assert re.match(
        r"^block-v1:.+\+.+\+.+type@openassessment+block@[a-f0-9]{32}$", field.item_id
    )


@custom_given(ORAGetSubmissionForStaffGradingEventField)
def test_models_edx_ora_get_submission_for_staff_grading_event_field_with_valid_values(
    field,
):
    """Tests that a valid `ORAGetSubmissionForStaffGradingEventField` does not raise a
    `ValidationError`."""

    assert re.match(
        r"^block-v1:.+\+.+\+.+type@openassessment+block@[a-f0-9]{32}$", field.item_id
    )


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


@custom_given(ORASaveSubmissionEventField)
def test_models_edx_ora_save_submission_event_field_with_valid_values(field):
    """Tests that a valid `ORASaveSubmissionEventField` does not raise a
    `ValidationError`.
    """

    if len(field.saved_response.parts) == 0:
        assert field.saved_response.parts == []

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
    "content_hash",
    [
        "d0d4a647742943e3951b45d9db8a0ea1ff71ae3&",
        "d0d4a647742943e3951b45d9db8a0ea1ff71ae360",
        "D0d4a647742943e3951b45d9db8a0ea1ff71ae36",
    ],
)
@custom_given(ORAAssessEventRubricField)
def test_models_edx_ora_assess_event_rubric_field_with_invalid_problem_id_value(
    content_hash, field
):
    """Tests that an invalid `problem_id` value in `ProblemCheckEventField` raises a
    `ValidationError`.
    """

    invalid_field = json.loads(field.json())
    invalid_field["content_hash"] = content_hash

    with pytest.raises(
        ValidationError, match="content_hash\n  string does not match regex"
    ):
        ORAAssessEventRubricField(**invalid_field)
