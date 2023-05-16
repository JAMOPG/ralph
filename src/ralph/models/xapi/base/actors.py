"""Base xAPI `Actor` definitions."""

from typing import List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import AnyUrl, StrictStr, constr

from ..config import BaseModelWithConfig
from .common import IRI, MailtoEmail


class BaseXapiAgentAccount(BaseModelWithConfig):
    """Pydantic model for `Agent` type account` property.

    Attributes:
        homePage (IRI): Consists of the home page of the account's service provider.
        name (str): Consists of the unique id or name of the Actor's account.
    """

    homePage: IRI
    name: StrictStr


# Actor with `Agent` ObjectType


class BaseXapiAgentCommonProperties(BaseModelWithConfig):
    """Pydantic model for core `Agent` type property.

    It defines who performed the action.

    Attributes:
        objectType (str): Consists of the value `Agent`.
        name (str): Consists of the full name of the Agent.
    """

    objectType: Optional[Literal["Agent"]]
    name: Optional[StrictStr]


class BaseXapiAgentWithMboxIFI(BaseXapiAgentCommonProperties):
    """Pydantic model for `Agent` type property.

    It defines a mailto Inverse Functional Identifier.

    Attributes:
        mbox (MailtoEmail): Consists of the Agent's email address.
    """

    mbox: MailtoEmail


class BaseXapiAgentWithMboxSha1SumIFI(BaseXapiAgentCommonProperties):
    """Pydantic model for `Agent` type property.

    It defines a hash Inverse Functional Identifier.

    Attributes:
        mbox_sha1sum (str): Consists of the SHA1 hash of the Agent's email address.
    """

    mbox_sha1sum: constr(regex=r"^[0-9a-f]{40}$")  # noqa:F722


class BaseXapiAgentWithOpenIdIFI(BaseXapiAgentCommonProperties):
    """Pydantic model for `Agent` type property.

    It defines an OpenID Inverse Functional Identifier.

    Attributes:
        openid (URI): Consists of an openID that uniquely identifies the Agent.
    """

    openid: AnyUrl


class BaseXapiAgentWithAccountIFI(BaseXapiAgentCommonProperties):
    """Pydantic model for `Agent` type property.

    It defines an account Inverse Functional Identifier.

    Attributes:
        account (dict): See AccountActorAccountField.
    """

    account: BaseXapiAgentAccount


BaseXapiAgent = Union[
    BaseXapiAgentWithMboxIFI,
    BaseXapiAgentWithMboxSha1SumIFI,
    BaseXapiAgentWithOpenIdIFI,
    BaseXapiAgentWithAccountIFI,
]


# Actor with `Group` ObjectType


class BaseXapiGroupCommonProperties(BaseModelWithConfig):
    """Pydantic model for core `Group` type property.

    It is defined the Group which performed the action.

    Attributes:
        objectType (str): Consists of the value `Group`.
        name (str): Consists of the full name of the Group.
        member (list): Consist of a list of the members of this Group.
    """

    objectType: Literal["Group"]
    name: Optional[StrictStr]


class BaseXapiAnonymousGroup(BaseXapiGroupCommonProperties):
    """Pydantic model for `Group` type property.

    It is defined for Anonymous Group type.

    Attributes:
        member (list): Consist of a list of the members of this Group.
    """

    member: List[BaseXapiAgent]


class BaseXapiIdentifiedGroup(BaseXapiGroupCommonProperties):
    """Pydantic model for `Group` type property.

    It is defined for Identified Group type.

    Attributes:
        member (list): Consist of a list of the members of this Group.
    """

    member: Optional[List[BaseXapiAgent]]


class BaseXapiIdentifiedGroupWithMboxIFI(
    BaseXapiIdentifiedGroup, BaseXapiAgentWithMboxIFI
):
    """Pydantic model for `Group` type property.

    It is defined for group type with a mailto IFI.
    """


class BaseXapiIdentifiedGroupWithMboxSha1SumIFI(
    BaseXapiIdentifiedGroup, BaseXapiAgentWithMboxSha1SumIFI
):
    """Pydantic model for `Group` type property.

    It is defined for group type with a hash IFI.
    """


class BaseXapiIdentifiedGroupWithOpenIdIFI(
    BaseXapiIdentifiedGroup, BaseXapiAgentWithOpenIdIFI
):
    """Pydantic model for `Group` type property.

    It is defined for group type with an openID IFI.
    """


class BaseXapiIdentifiedGroupWithAccountIFI(
    BaseXapiIdentifiedGroup, BaseXapiAgentWithOpenIdIFI
):
    """Pydantic model for `Group` type property.

    It is defined for group type with an account IFI.
    """


BaseXapiGroup = Union[
    BaseXapiAnonymousGroup,
    BaseXapiIdentifiedGroupWithMboxIFI,
    BaseXapiIdentifiedGroupWithMboxSha1SumIFI,
    BaseXapiIdentifiedGroupWithOpenIdIFI,
    BaseXapiIdentifiedGroupWithAccountIFI,
]
BaseXapiActor = Union[BaseXapiAgent, BaseXapiGroup]
