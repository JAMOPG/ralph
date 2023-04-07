"""Base xAPI `Actor` definitions."""

from typing import List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import AnyUrl, StrictStr, constr

from ..config import BaseModelWithConfig
from .common import IRI, MailtoEmail


class BaseXapiAgentTypeAccount(BaseModelWithConfig):
    """Pydantic model for `Agent` type account` property.

    Attributes:
        homePage (IRI): Consists of the home page of the account's service provider.
        name (str): Consists of the unique id or name of the Actor's account.
    """

    homePage: IRI
    name: StrictStr


# Actor with `Agent` ObjectType


class BaseXapiAgentTypeCommonProperties(BaseModelWithConfig):
    """Pydantic model for core `Agent` type property.

    It defines who performed the action.

    Attributes:
        objectType (str): Consists of the value `Agent`.
        name (str): Consists of the full name of the Agent.
    """

    objectType: Optional[Literal["Agent"]]
    name: Optional[StrictStr]


class BaseXapiAgentTypeWithMboxIFI(BaseXapiAgentTypeCommonProperties):
    """Pydantic model for `Agent` type property.

    It defines a mailto Inverse Functional Identifier.

    Attributes:
        mbox (MailtoEmail): Consists of the Agent's email address.
    """

    mbox: MailtoEmail


class BaseXapiAgentTypeWithMboxSha1SumIFI(BaseXapiAgentTypeCommonProperties):
    """Pydantic model for `Agent` type property.

    It defines a hash Inverse Functional Identifier.

    Attributes:
        mbox_sha1sum (str): Consists of the SHA1 hash of the Agent's email address.
    """

    mbox_sha1sum: constr(regex=r"^[0-9a-f]{40}$")  # noqa:F722


class BaseXapiAgentTypeWithOpenIdIFI(BaseXapiAgentTypeCommonProperties):
    """Pydantic model for `Agent` type property.

    It defines an OpenID Inverse Functional Identifier.

    Attributes:
        openid (URI): Consists of an openID that uniquely identifies the Agent.
    """

    openid: AnyUrl


class BaseXapiAgentTypeWithAccountIFI(BaseXapiAgentTypeCommonProperties):
    """Pydantic model for `Agent` type property.

    It defines an account Inverse Functional Identifier.

    Attributes:
        account (dict): See AccountActorAccountField.
    """

    account: BaseXapiAgentTypeAccount


BaseXapiAgentType = Union[
    BaseXapiAgentTypeWithMboxIFI,
    BaseXapiAgentTypeWithMboxSha1SumIFI,
    BaseXapiAgentTypeWithOpenIdIFI,
    BaseXapiAgentTypeWithAccountIFI,
]


# Actor with `Group` ObjectType


class BaseXapiGroupTypeCommonProperties(BaseModelWithConfig):
    """Pydantic model for core `Group` type property.

    It is defined the Group which performed the action.

    Attributes:
        objectType (str): Consists of the value `Group`.
        name (str): Consists of the full name of the Group.
        member (list): Consist of a list of the members of this Group.
    """

    objectType: Literal["Group"]
    name: Optional[StrictStr]


class BaseXapiAnonymousGroupType(BaseXapiGroupTypeCommonProperties):
    """Pydantic model for `Group` type property.

    It is defined for Anonymous Group type.

    Attributes:
        member (list): Consist of a list of the members of this Group.
    """

    member: List[BaseXapiAgentType]


class BaseXapiIdentifiedGroupType(BaseXapiGroupTypeCommonProperties):
    """Pydantic model for `Group` type property.

    It is defined for Identified Group type.

    Attributes:
        member (list): Consist of a list of the members of this Group.
    """

    member: Optional[List[BaseXapiAgentType]]


class BaseXapiIdentifiedGroupTypeWithMboxIFI(
    BaseXapiIdentifiedGroupType, BaseXapiAgentTypeWithMboxIFI
):
    """Pydantic model for `Group` type property.

    It is defined for group type with a mailto IFI.
    """


class BaseXapiIdentifiedGroupTypeWithMboxSha1SumIFI(
    BaseXapiIdentifiedGroupType, BaseXapiAgentTypeWithMboxSha1SumIFI
):
    """Pydantic model for `Group` type property.

    It is defined for group type with a hash IFI.
    """


class BaseXapiIdentifiedGroupTypeWithOpenIdIFI(
    BaseXapiIdentifiedGroupType, BaseXapiAgentTypeWithOpenIdIFI
):
    """Pydantic model for `Group` type property.

    It is defined for group type with an openID IFI.
    """


class BaseXapiIdentifiedGroupTypeWithAccountIFI(
    BaseXapiIdentifiedGroupType, BaseXapiAgentTypeWithOpenIdIFI
):
    """Pydantic model for `Group` type property.

    It is defined for group type with an account IFI.
    """


BaseXapiGroupType = Union[
    BaseXapiAnonymousGroupType,
    BaseXapiIdentifiedGroupTypeWithMboxIFI,
    BaseXapiIdentifiedGroupTypeWithMboxSha1SumIFI,
    BaseXapiIdentifiedGroupTypeWithOpenIdIFI,
    BaseXapiIdentifiedGroupTypeWithAccountIFI,
]
BaseXapiActor = Union[BaseXapiAgentType, BaseXapiGroupType]
