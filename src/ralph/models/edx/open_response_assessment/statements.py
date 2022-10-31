"""Open Response Assessment events model definitions."""

from typing import Literal

from ralph.models.edx.server import BaseServerModel
from ralph.models.selector import selector

from .fields.events import (
    ORAAssessEventField,
    ORACreateSubmissionEventField,
    ORAGetPeerSubmissionEventField,
    ORAGetSubmissionForStaffGradingEventField,
    ORASaveSubmissionEventField,
    ORAStudentTrainingAssessExampleEventField,
    ORASubmitFeedbackOnAssessmentsEventField,
    ORAUploadFileEventField,
)


class ORAGetPeerSubmission(BaseServerModel):
    """Represents the `openassessmentblock.get_peer_submission` event.

    Attributes:
        event (dict): See ORAGetPeerSubmissionEventField.
        event_type (str): Consists of the value
            `openassessmentblock.get_peer_submission`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server", event_type="openassessmentblock.get_peer_submission"
    )

    event: ORAGetPeerSubmissionEventField
    event_type: Literal["openassessmentblock.get_peer_submission"]
    page: Literal["x_module"]


class ORAGetSubmissionForStaffGrading(BaseServerModel):
    """Represents the `openassessmentblock.get_submission_for_staff_grading` event.

    Attributes:
        event (dict): See ORAGetSubmissionForStaffGradingEventField.
        event_type (str): Consists of the value
            `openassessmentblock.get_submission_for_staff_grading`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server",
        event_type="openassessmentblock.get_submission_for_staff_grading",
    )

    event: ORAGetSubmissionForStaffGradingEventField
    event_type: Literal["openassessmentblock.get_submission_for_staff_grading"]
    page: Literal["x_module"]


class ORAPeerAssess(BaseServerModel):
    """Represents the `openassessmentblock.peer_assess` event.

    Attributes:
        event (dict): See ORAAssessEventField.
        event_type (str): Consists of the value `openassessmentblock.peer_assess`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server", event_type="openassessmentblock.peer_assess"
    )

    event: ORAAssessEventField
    event_type: Literal["openassessmentblock.peer_assess"]
    page: Literal["x_module"]


class ORASelfAssess(BaseServerModel):
    """Represents the `openassessmentblock.self_assess` event.

    Attributes:
        event (dict): See ORAAssessEventField.
        event_type (str): Consists of the value `openassessmentblock.self_assess`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server", event_type="openassessmentblock.self_assess"
    )

    event: ORAAssessEventField
    event_type: Literal["openassessmentblock.self_assess"]
    page: Literal["x_module"]


class ORAStaffAssess(BaseServerModel):
    """Represents the `openassessmentblock.staff_assess` event.

    Attributes:
        event (dict): See ORAStaffAssessEventField.
        event_type (str): Consists of the value `openassessmentblock.staff_assess`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server", event_type="openassessmentblock.staff_assess"
    )

    event: ORAAssessEventField
    event_type: Literal["openassessmentblock.staff_assess"]
    page: Literal["x_module"]


class ORASubmitFeedbackOnAssessments(BaseServerModel):
    """Represents the `openassessmentblock.submit_feedback_on_assessments` event.

    Attributes:
        event (dict): See ORASubmitFeedbackOnAssessmentsEventField.
        event_type (str): Consists of the value
            `openassessmentblock.submit_feedback_on_assessments`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server",
        event_type="openassessmentblock.submit_feedback_on_assessments",
    )

    event: ORASubmitFeedbackOnAssessmentsEventField
    event_type: Literal["openassessmentblock.submit_feedback_on_assessments"]
    page: Literal["x_module"]


class ORACreateSubmission(BaseServerModel):
    """Represents the `openassessmentblock.create_submission` event.

    Attributes:
        event (dict): See ORACreateSubmissionEventField.
        event_type (str): Consists of the value `openassessmentblock.create_submission`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server", event_type="openassessmentblock.create_submission"
    )

    event: ORACreateSubmissionEventField
    event_type: Literal["openassessmentblock.create_submission"]
    page: Literal["x_module"]


class ORASaveSubmission(BaseServerModel):
    """Represents the `openassessmentblock.save_submission` event.

    This event is triggered when the user clicks on the <kbd>Save your progress</kbd>
    button to save the current state of his response to an open assessment question.

    Attributes:
        event (str): See ORASaveSubmissionEventField.
        event_type (str): Consists of the value `openassessmentblock.save_submission`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server", event_type="openassessmentblock.save_submission"
    )

    event: ORASaveSubmissionEventField
    event_type: Literal["openassessmentblock.save_submission"]
    page: Literal["x_module"]


class ORAStudentTrainingAssessExample(BaseServerModel):
    """Represents the `openassessment.student_training_assess_example` event.

    Attributes:
        event (dict): See ORAStudentTrainingAssessExampleEventField.
        event_type (str): Consists of the value
            `openassessment.student_training_assess_example`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server",
        event_type="openassessment.student_training_assess_example",
    )

    event: ORAStudentTrainingAssessExampleEventField
    event_type: Literal["openassessment.student_training_assess_example"]
    page: Literal["x_module"]


class ORAUploadFile(BaseServerModel):
    """Represents the `openassessment.upload_file` event.

    Attributes:
        event (dict): See ORAUploadFileEventField.
        event_type (str): Consists of the value `openassessment.upload_file`.
        page (str): Consists of the value `x_module`.
    """

    __selector__ = selector(
        event_source="server", event_type="openassessment.upload_file"
    )

    event: ORAUploadFileEventField
    event_type: Literal["openassessment.upload_file"]
    page: Literal["x_module"]
