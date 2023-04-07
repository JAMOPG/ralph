"""Tests for the base xAPI `Actor` definitions."""

import json
import re

import pytest
from pydantic import ValidationError

from ralph.models.xapi.base.actors import (
    BaseXapiAgentTypeWithMboxSha1SumIFI,
    BaseXapiGroupTypeCommonProperties,
)

from tests.fixtures.hypothesis_strategies import custom_given


@custom_given(BaseXapiAgentTypeWithMboxSha1SumIFI)
def test_models_xapi_base_actor_agent_type_with_mbox_sha1_sum_ifi_with_valid_field(
    field,
):
    """Tests a valid BaseXapiAgentTypeWithMboxSha1SumIFI has the expected
    `mbox_sha1sum` regex.
    """

    assert re.match(r"^[0-9a-f]{40}$", field.mbox_sha1sum)


@pytest.mark.parametrize(
    "mbox_sha1sum",
    [
        "1baccll9xkidkd4re9n24djgfh939g7dhyjm3li3",
        "1baccde9",
        "1baccdd9abcdfd4ae9b24dedfa939c7deffa3db3a7",
    ],
)
@custom_given(BaseXapiAgentTypeWithMboxSha1SumIFI)
def test_models_xapi_base_actor_agent_type_with_mbox_sha1_sum_ifi_with_invalid_field(
    mbox_sha1sum, field
):
    """Tests an invalid `mbox_sha1sum` property in
    BaseXapiAgentTypeWithMboxSha1SumIFI raises a `ValidationError`.
    """

    invalid_field = json.loads(field.json())
    invalid_field["mbox_sha1sum"] = mbox_sha1sum

    with pytest.raises(
        ValidationError, match="mbox_sha1sum\n  string does not match regex"
    ):
        BaseXapiAgentTypeWithMboxSha1SumIFI(**invalid_field)


@custom_given(BaseXapiGroupTypeCommonProperties)
def test_models_xapi_base_actor_group_type_common_properties_with_valid_field(
    field,
):
    """Tests a valid BaseXapiGroupTypeCommonProperties has the expected
    `objectType` value.
    """

    assert field.objectType == "Group"
