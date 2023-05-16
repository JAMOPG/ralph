"""`Virtual classroom` verbs definitions."""

from typing import Dict

from ...base.verbs import BaseXapiVerb
from ...constants import LANG_EN_US_DISPLAY
from ..constants.virtual_classroom import (
    LOWERED_HAND_VERB_DISPLAY,
    LOWERED_HAND_VERB_ID,
    MUTED_VERB_DISPLAY,
    MUTED_VERB_ID,
    RAISED_HAND_VERB_DISPLAY,
    RAISED_HAND_VERB_ID,
    SHARED_SCREEN_VERB_DISPLAY,
    SHARED_SCREEN_VERB_ID,
    STARTED_CAMERA_VERB_DISPLAY,
    STARTED_CAMERA_VERB_ID,
    STOPPED_CAMERA_VERB_DISPLAY,
    STOPPED_CAMERA_VERB_ID,
    UNMUTED_VERB_DISPLAY,
    UNMUTED_VERB_ID,
    UNSHARED_SCREEN_VERB_DISPLAY,
    UNSHARED_SCREEN_VERB_ID,
)


class MutedVerb(BaseXapiVerb):
    """Pydantic model for muted `verb`.

    Attributes:
        id (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/verbs/muted`.
        display (dict): Consists of the dictionary `{"en-US": "muted"}`.
    """

    id: MUTED_VERB_ID = MUTED_VERB_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, MUTED_VERB_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: MUTED_VERB_DISPLAY.__args__[0]
    }


class UnmutedVerb(BaseXapiVerb):
    """Pydantic model for unmuted `verb`.

    Attributes:
        id (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/verbs/unmuted`.
        display (dict): Consists of the dictionary `{"en-US": "unmuted"}`.
    """

    id: UNMUTED_VERB_ID = UNMUTED_VERB_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, UNMUTED_VERB_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: UNMUTED_VERB_DISPLAY.__args__[0]
    }


class StartedCameraVerb(BaseXapiVerb):
    """Pydantic model for started camera `verb`.

    Attributes:
        id (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/verbs/started-camera`.
        display (dict): Consists of the dictionary `{"en-US": "started camera"}`.
    """

    id: STARTED_CAMERA_VERB_ID = STARTED_CAMERA_VERB_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, STARTED_CAMERA_VERB_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: STARTED_CAMERA_VERB_DISPLAY.__args__[0]
    }


class StoppedCameraVerb(BaseXapiVerb):
    """Pydantic model for stopped camera `verb`.

    Attributes:
        id (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/verbs/stopped-camera`.
        display (dict): Consists of the dictionary `{"en-US": "stopped camera"}`.
    """

    id: STOPPED_CAMERA_VERB_ID = STOPPED_CAMERA_VERB_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, STOPPED_CAMERA_VERB_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: STOPPED_CAMERA_VERB_DISPLAY.__args__[0]
    }


class SharedScreenVerb(BaseXapiVerb):
    """Pydantic model for shared screen `verb`.

    Attributes:
        id (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/verbs/shared-screen`.
        display (dict): Consists of the dictionary `{"en-US": "shared screen"}`.
    """

    id: SHARED_SCREEN_VERB_ID = SHARED_SCREEN_VERB_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, SHARED_SCREEN_VERB_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: SHARED_SCREEN_VERB_DISPLAY.__args__[0]
    }


class UnsharedScreenVerb(BaseXapiVerb):
    """Pydantic model for unshared screen `verb`.

    Attributes:
        id (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/verbs/unshared-screen`.
        display (dict): Consists of the dictionary `{"en-US": "unshared screen"}`.
    """

    id: UNSHARED_SCREEN_VERB_ID = UNSHARED_SCREEN_VERB_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, UNSHARED_SCREEN_VERB_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: UNSHARED_SCREEN_VERB_DISPLAY.__args__[0]
    }


class RaisedHandVerb(BaseXapiVerb):
    """Pydantic model for raised hand `verb`.

    Attributes:
        id (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/verbs/raised-hand`.
        display (dict): Consists of the dictionary `{"en-US": "raised hand"}`.
    """

    id: RAISED_HAND_VERB_ID = RAISED_HAND_VERB_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, RAISED_HAND_VERB_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: RAISED_HAND_VERB_DISPLAY.__args__[0]
    }


class LoweredHandVerb(BaseXapiVerb):
    """Pydantic model for lowered hand `verb`.

    Attributes:
        id (str): Consists of the value
            `https://w3id.org/xapi/virtual-classroom/verbs/lowered-hand`.
        display (dict): Consists of the dictionary `{"en-US": "lowered hand"}`.
    """

    id: LOWERED_HAND_VERB_ID = LOWERED_HAND_VERB_ID.__args__[0]
    display: Dict[LANG_EN_US_DISPLAY, LOWERED_HAND_VERB_DISPLAY] = {
        LANG_EN_US_DISPLAY.__args__[0]: LOWERED_HAND_VERB_DISPLAY.__args__[0]
    }
