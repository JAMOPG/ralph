"""Base xAPI `Object` definitions (2)."""

# Nota bene: we split object definitions into `objects.py` and `unnested_objects.py`
# because of the circular dependency : objects -> context -> objects.

from datetime import datetime
from typing import List, Optional, Union

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

from pydantic import Field

from ..config import BaseExtensionModelWithConfig, BaseModelWithConfig
from ..constants import EXTENSION_COURSE_ID, EXTENSION_MODULE_ID, EXTENSION_SCHOOL_ID
from .actors import BaseXapiActor, BaseXapiAgent, BaseXapiGroup
from .attachments import BaseXapiAttachment
from .contexts import BaseXapiContext
from .results import BaseXapiResult
from .unnested_objects import BaseXapiUnnestedObject
from .verbs import BaseXapiVerb


class BaseXapiSubStatementType(BaseModelWithConfig):
    """Pydantic model for `SubStatement` type property.

    Attributes:
        actor (dict): See BaseXapiActor.
        verb (dict): See BaseXapiVerb.
        object (dict): See BaseXapiUnnestedObject.
        objecType (dict): Consists of the value `SubStatement`.
    """

    actor: BaseXapiActor
    verb: BaseXapiVerb
    object: BaseXapiUnnestedObject
    objectType: Literal["SubStatement"]
    result: Optional[BaseXapiResult]
    context: Optional[BaseXapiContext]
    timestamp: Optional[datetime]
    attachments: Optional[List[BaseXapiAttachment]]


BaseXapiObject = Union[
    BaseXapiUnnestedObject,
    BaseXapiSubStatementType,
    BaseXapiAgent,
    BaseXapiGroup,
]


# TO BE REMOVED
class ObjectDefinitionExtensionsField(BaseExtensionModelWithConfig):
    """Pydantic model for `object`.`definition`.`extensions` property.

    Attributes:
        school (str): Consists of the name of the school.
        course (str): Consists of the name of the course.
        module (str): Consists of the name of the module.
    """

    school: Optional[str] = Field(alias=EXTENSION_SCHOOL_ID)
    course: Optional[str] = Field(alias=EXTENSION_COURSE_ID)
    module: Optional[str] = Field(alias=EXTENSION_MODULE_ID)
