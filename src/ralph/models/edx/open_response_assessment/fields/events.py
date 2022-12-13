"""Open Response Assessment events model event fields definitions."""

from datetime import datetime
from typing import Literal, Union
from uuid import UUID

from pydantic import Json, constr

from ralph.models.edx.base import AbstractBaseEventField, BaseModelWithConfig


class ORAGetPeerSubmissionEventField(AbstractBaseEventField):
    """Pydantic model for `openassessmentblock.get_peer_submission`.`event` field.

    Attributes:
        course_id (str): Consists of the course identifier including the assessment.
        item_id (str): Consists of the locator string that identifies the problem in
            the course.
        requesting_student_id (str): Consists of the course-specific anonymized user ID
            of the learner who retrieved the response for peer assessment.
        submission_returned_uuid (str): Consists of the unique identifier of the
            response that was retrieved for assessment. Set to `None` if no assessment
            available.
    """

    course_id: constr(max_length=255)
    item_id: constr(
        regex=(
            r"^block-v1:.+\+.+\+.+type@openassessment"  # noqa : F722
            r"+block@[a-f0-9]{32}$"  # noqa : F722
        )
    )
    requesting_student_id: str
    submission_returned_uuid: Union[str, None]


class ORAGetSubmissionForStaffGradingEventField(AbstractBaseEventField):
    """Pydantic model for `openassessmentblock.get_submission_for_staff_grading`.`event` field.

    Attributes:
        course_id (str): Consists of the course identifier including the assessment.
        item_id (str): Consists of the locator string that identifies the problem in
            the course.
        requesting_student_id (str): Consists of the course-specific anonymized user ID
            of the learner who retrieved the response for peer assessment.
        submission_returned_uuid (str): Consists of the unique identifier of the
            response that was retrieved for assessment. Set to `None` if no assessment
            available.
        requesting_staff_id (str): Consists of the course-specific anonymized user ID
            of the course team member who is retrieved the response for grading.
    """

    course_id: constr(max_length=255)
    item_id: constr(
        regex=(
            r"^block-v1:.+\+.+\+.+type@openassessment"  # noqa : F722
            r"+block@[a-f0-9]{32}$"  # noqa : F722
        )
    )
    requesting_student_id: str
    submission_returned_uuid: Union[str, None]
    requesting_staff_id: str
    type: str


class ORAAssessEventRubricField(BaseModelWithConfig):
    """Pydantic model for assessment `event`.`rubric` field.

    This field is defined in:
    - `openassessmentblock.peer_assess`
    - `openassessmentblock.self_assess`
    - `openassessmentblock.staff_assess`

    Attributes:
        content_hash: Consists of the identifier of the rubric that the learner used to
            assess the response.
    """

    content_hash: constr(regex=r"^[a-f0-9]{1,40}$")  # noqa: F722


class ORAAssessEventField(AbstractBaseEventField):
    """Pydantic model for assessment `event` field.

    This field is defined in:
        - `openassessmentblock.peer_assess`
        - `openassessmentblock.self_assess`
        - `openassessmentblock.staff_assess`

    Attributes:
        feedback (str): Consists of the learner's comments about the submitted response.
        parts (array): Consists of a list that contains for each criterion the option
            that the learner selected for it, and any feedback comments that the learner
            supplied.
        rubric (dict): see ORAPeerAssessEventRubricField.
        scored_at (datetime): Consists of the timestamp for when the assessment was
            submitted.
        scorer_id (str): Consists of the course-specific anonymized user ID of the
            learner who submitted the assessment.
        score_type (str): Consists of either `PE` value for a peer assessment, `SE` for
            a self assessment or `ST` for a staff assessment.
        submission_uuid (str): Consists of the unique identifier for the submitted
            response.
    """

    feedback: str
    parts: list[dict]
    rubric: ORAAssessEventRubricField
    scored_at: datetime
    scorer_id: constr(max_length=40)
    score_type: Literal["PE", "SE", "ST"]
    submission_uuid: UUID


class ORAStaffAssessEventField(ORAAssessEventField):
    """Pydantic model for `openassessmentblock.staff_assess`.`event` field.

    Attributes:
        type (str): Consists of the type of staff grading that is being performed. Can
            be either equalt to `regrade` in the case of a grade override or
            `full-grade` in the case of an included staff assessment step.
    """

    type: Literal["regrade", "full-grade"]


class ORASubmitFeedbackOnAssessmentsEventField(AbstractBaseEventField):
    """Pydantic modelf for `openassessmentblock.submit_feedback_on_assessments`.`event` field.

    Attributes:
        feedback_text (str): Consists of the learner's comments about the assessment
            process.
        options (array): Consists of the label of each checkbox option that the learner
            selected to evaluate the assessment process.
        submission_uuid (str): Consists of the unique identifier for for the feedback.
    """

    feedback_text: str
    options: list[str]
    submission_uuid: UUID


class ORACreateSubmissionEventAnswerField(BaseModelWithConfig):
    """Pydantic model for `openassessmentblock.create_submission`.`event`.`answer` field.

    Attributes:
        text (str): Consists of the answer field.
        file_upload_key (str): Consists of AWS S3 key identifying the location of the
            uploaded file on the Amazon S3 storage service. Only used when an answer
            includes files.
    """

    text: str
    file_upload_key: str


class ORACreateSubmissionEventField(AbstractBaseEventField):
    """Pydantic model for `openassessmentblock.create_submission`.`event` field.

    Attributes:
        answer (dict): see ORACreateSubmissionEventAnswerField.
        attempt_number (int): Consists of the number of submission attempts. Currently,
            this value is set to 1.
        created_at (datetime): Consists of the timestamp for when the learner submitted
            the response.
        submitted_at (datetime): Consists of the timestamp for when the learner
            submitted the response. This value is the same as `submitted_at`.
        submission_uuid (str): Consists of the unique identifier of the response.
    """

    answer: ORACreateSubmissionEventAnswerField
    attempt_number: int
    created_at: datetime
    submitted_at: datetime
    submission_uuid: UUID


class ORASaveSubmissionEventSavedResponseField(BaseModelWithConfig):
    """Pydantic model for `openassessmentblock.save_submission`.`saved_response` field.

    Attributes:
        parts (list): Consists of a list of dictionaries `{"text": <response value>}`.
    """

    parts: list[dict[Literal["text"], str]]


class ORASaveSubmissionEventField(AbstractBaseEventField):
    """Pydantic model for `openassessmentblock.save_submission`.`event` field.

    Attributes:
        saved_response (str): Consists of a JSON string of the users saved responses.
            Note:
                Responses have a length limit of 100000 in the front-end but not in the
                back-end. Events are truncated at `TRACK_MAX_EVENT` which is 50000 by
                default. Also the `eventtracking.backends.logger.LoggerBackend`
                silently drops events when they exceed `TRACK_MAX_EVENT`.
    """

    # pylint: disable=unsubscriptable-object
    saved_response: Union[
        Json[ORASaveSubmissionEventSavedResponseField],
        ORASaveSubmissionEventSavedResponseField,
    ]


class ORAStudentTrainingAssessExampleEventField(AbstractBaseEventField):
    """Pydantic model for `openassessment.student_training_assess_example`.`event` field.

    Attributes:
        corrections (dict): Consists of a set of name/value pairs that identify
            criteria for which the learner selected a different option than the course
            team.
        options_selected (dict): Consists of a set of name/value pairs that identify
            the option that the learner selected for each criterion in the rubric.
        submission_uuid (str): Consists of the unique identifier of the response.
    """

    corrections: dict[str, str]
    options_selected: dict[str, str]
    submission_uuid: UUID


class ORAUploadFileEventField(BaseModelWithConfig):
    """Pydantic model for `openassessment.upload_file`.`event` field.

    Attributes:
        fileName (str): Consists of the name of the uploaded file.
        fileSize (int): Consists of the bytes size of the uploaded file.
        fileType (str): Consists of the MIME type of the uploaded file.
    """

    fileName: constr(max_length=255)
    fileSize: int
    fileType: str
