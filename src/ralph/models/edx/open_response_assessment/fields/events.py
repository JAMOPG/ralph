"""Open Response Assessment events model event fields definitions."""

from datetime import datetime
from typing import Literal, Union

from pydantic import Json, constr

from ralph.models.edx.base import AbstractBaseEventField, BaseModelWithConfig


class ORAGetPeerSubmissionEventField(AbstractBaseEventField):
    """Represents the `event` field of `openassessmentblock.get_peer_submission` model.

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
    item_id: constr(max_length=128)
    requesting_student_id: str
    submission_returned_uuid: str


class ORAGetSubmissionForStaffGradingEventField(AbstractBaseEventField):
    """Represents the `event` field of `openassessmentblock.get_peer_submission` model.

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
    item_id: constr(max_length=128)
    requesting_student_id: str
    submission_returned_uuid: str
    requesting_staff_id: str
    type: str


class ORAAssessEventRubricField(BaseModelWithConfig):
    """Represents `the event.rubric` field for assessment events.

    This field is defined in:
    - `openassessmentblock.peer_assess`
    - `openassessmentblock.self_assess`
    - `openassessmentblock.staff_assess`

    Attributes:
        contenthash: Consists of the identifier of the rubric that the learner used to
            assess the response.
    """

    contenthash: Union[constr(regex=r"^[a-f0-9]{1,40}$"), Literal[""]]  # noqa: F722


class ORAAssessEventField(AbstractBaseEventField):
    """Represents the core `event` field for assessment events.

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

    feedback: constr(max_length=10000)
    parts: list[dict]
    rubric: ORAAssessEventRubricField
    scored_at: datetime
    scorer_id: constr(max_length=40)
    score_type: Union[Literal["PE"], Literal["SE"], Literal["ST"]]
    submission_uuid: constr(max_length=128)


class ORAStaffAssessEventField(ORAAssessEventField):
    """Represents the `event` field of `openassessmentblock.self_assess` event.

    Attributes:
        type (str): Consists of the type of staff grading that is being performed. Can
            be either `regrade` value in the case of a grade override or `full-grade`
            in the case of an included staff assessment step.
    """

    type: Union[Literal["regrade"], Literal["full-grade"]]


class ORASubmitFeedbackOnAssessmentsEventField(AbstractBaseEventField):
    """Represents the `event` field of
    `openassessmentblock.submit_feedback_on_assessments` event.

    Attributes:
        feedback_text (str): Consists of the learner's comments about the assessment
            process.
        options (array): Consists of the label of each checkbox option that the learner
            selected to evaluate the assessment process.
        submission_uuid (str): Consists of the unique identifier for for the feedback.
    """

    feedback_text: constr(max_length=10000)
    options: list
    submission_uuid: constr(max_length=128)


class ORACreateSubmissionEventAnswerField(BaseModelWithConfig):
    """Represents the `event.answer` field of `openassessmentblock.save_submission`
    model.

    Attributes:
        text (str): Consists of the answer field.
        file_upload_key (str): Consists of AWS S3 key identifying the location of the
            uploaded file on the Amazon S3 storage service. Only used when an answer
            includes files.
    """

    text: str
    file_upload_key: str


class ORACreateSubmissionEventField(AbstractBaseEventField):
    """Represents the `event` field of `openassessmentblock.save_submission` model.

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
    attempt_number: Literal[1]
    created_at: datetime
    submitted_at: datetime
    submission_uuid: constr(max_length=128)


class ORASaveSubmissionEventSavedResponseField(BaseModelWithConfig):
    """Represents the `openassessmentblock.save_submission` event `saved_response`
    field.

    Attributes:
        parts (list): Consists of a list of dictionaries `{"text": <response value>}`.
    """

    parts: list[dict[Literal["text"], str]]


class ORASaveSubmissionEventField(AbstractBaseEventField):
    """Represents the `event` field of `openassessmentblock.save_submission` model.

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
    """Represents the `event` field of `openassessment.student_training_assess_example`
    model.

    Attributes:
        corrections (dict): Consists of a set of name/value pairs that identify
            criteria for which the learner selected a different option than the course
            team.
        options_selected (dict): Consists of a set of name/value pairs that identify
            the option that the learner selected for each criterion in the rubric.
        submission_uuid (str): Consists of the unique identifier of the response.
    """

    corrections: dict
    options_selected: dict
    submission_uuid: constr(max_length=128)


class ORAUploadFileEventField(BaseModelWithConfig):
    """Represents the `event` field of `openassessment.upload_file` model.

    Attributes:
        fileName (str): Consists of the name of the uploaded file.
        fileSize (int): Consists of the bytes size of the uploaded file.
        fileType (str): Consists of the MIME type of the uploaded file.
    """

    fileName: constr(max_length=255)
    fileSize: int
    fileType: str
