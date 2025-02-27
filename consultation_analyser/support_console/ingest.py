import json
import logging

import boto3
from django.conf import settings

from consultation_analyser.consultations.models import (
    Answer,
    Consultation,
    ExecutionRun,
    Framework,
    Question,
    QuestionPart,
    Respondent,
    SentimentMapping,
    Theme,
    ThemeMapping,
)

logger = logging.getLogger("import")


STANCE_MAPPING = {
    "POSITIVE": ThemeMapping.Stance.POSITIVE,
    "NEGATIVE": ThemeMapping.Stance.NEGATIVE,
}

SENTIMENT_MAPPING = {
    "agreement": SentimentMapping.Position.AGREEMENT,
    "disagreement": SentimentMapping.Position.DISAGREEMENT,
    "unclear": SentimentMapping.Position.UNCLEAR,
}


def get_all_folder_names_within_folder(folder_name: str, bucket_name: str) -> set:
    s3 = boto3.resource("s3")
    objects = s3.Bucket(bucket_name).objects.filter(Prefix=folder_name)
    set_object_names = {obj.key for obj in objects}
    # Folders end in slash
    folders_only = {name for name in set_object_names if name.endswith("/")}
    # Exclude the name for the folder itself
    folder_names = {name.split("/")[1] for name in folders_only}
    folder_names = folder_names - {""}
    return folder_names


def list_all_files_in_folder(folder_name: str, bucket_name: str) -> set:
    s3 = boto3.resource("s3")
    objects = s3.Bucket(bucket_name).objects.filter(Prefix=folder_name)
    object_names = {obj.key for obj in objects}
    files_only = {name for name in object_names if not name.endswith("/")}
    return files_only


def get_themefinder_outputs_for_question(key: str) -> dict:
    s3 = boto3.client(
        "s3",
    )
    response = s3.get_object(Bucket=settings.AWS_BUCKET_NAME, Key=key)
    return json.loads(response["Body"].read())


def import_themes(question_part: QuestionPart, theme_data: dict) -> Framework:
    theme_generation_execution_run = ExecutionRun.objects.create(
        type=ExecutionRun.TaskType.THEME_GENERATION
    )
    framework = Framework.create_initial_framework(
        question_part=question_part, execution_run=theme_generation_execution_run
    )
    for theme_key, theme_value in theme_data.items():
        name, description = theme_value.split(": ", 1)
        Theme.create_initial_theme(
            framework=framework, key=theme_key, name=name, description=description
        )
    return framework


def get_theme_for_key(framework: Framework, key: str) -> Theme:
    return Theme.objects.get(framework=framework, key=key)


def import_theme_mapping_and_responses(
    framework: Framework,
    sentiment_execution_run: ExecutionRun,
    mapping_execution_run: ExecutionRun,
    theme_mapping_dict: dict,
) -> None:
    # TODO - check unique IDs
    question_part = framework.question_part
    consultation = question_part.question.consultation

    # Create respondent if doesn't exist, then create answer
    response_id = theme_mapping_dict["response_id"]
    respondent, _ = Respondent.objects.get_or_create(
        consultation=consultation, themefinder_respondent_id=response_id
    )

    # Create the answer
    # TODO -  we should change the output format in themefinder
    # At the moment it is of the form `question_0`
    keys = [key for key in theme_mapping_dict.keys() if key.startswith("question_")]
    relevant_key = keys[0]  # Can assume just one
    text = theme_mapping_dict[relevant_key]
    answer = Answer.objects.create(question_part=question_part, respondent=respondent, text=text)

    # Then add the sentiment to the answer
    raw_position = theme_mapping_dict["position"]
    position = SENTIMENT_MAPPING.get(raw_position, "")
    SentimentMapping.objects.create(
        answer=answer, position=position, execution_run=sentiment_execution_run
    )

    # Then map the themes to the answer
    reasons = theme_mapping_dict["reasons"]
    labels = theme_mapping_dict["labels"]
    stances = theme_mapping_dict["stances"]

    for reason, label, raw_stance in zip(reasons, labels, stances):
        theme = get_theme_for_key(framework, label)
        stance = STANCE_MAPPING.get(raw_stance, "")
        ThemeMapping(
            answer=answer,
            theme=theme,
            reason=reason,
            stance=stance,
            execution_run=mapping_execution_run,
        ).save()


def import_theme_mappings_for_framework(framework: Framework, list_mappings: list[dict]) -> None:
    sentiment_execution_run = ExecutionRun.objects.create(
        type=ExecutionRun.TaskType.SENTIMENT_ANALYSIS
    )
    mapping_execution_run = ExecutionRun.objects.create(type=ExecutionRun.TaskType.THEME_MAPPING)
    for theme_mapping_dict in list_mappings:
        import_theme_mapping_and_responses(
            framework=framework,
            sentiment_execution_run=sentiment_execution_run,
            mapping_execution_run=mapping_execution_run,
            theme_mapping_dict=theme_mapping_dict,
        )


# TODO - will change this to pass in a consultation
# This does it for one question
# TODO - key of form
# app_data/<consultation_folder>/<timestamped_folder>/question_n/something.json
def import_themefinder_data_for_question_part(key: str) -> None:
    # TODO - check for different IDs
    consultation = Consultation.objects.create(title="MY IMPORT")
    data = get_themefinder_outputs_for_question(key)
    question_text = data["question"]

    # TODO - think about where to store text - in Question or QuestionPart
    # Put it in the new question for now
    question = Question.objects.create(consultation=consultation, text=question_text)
    question_part = QuestionPart.objects.create(text="", question=question)

    # Now import themes
    refined_themes = data["refined_themes"][0]
    framework = import_themes(question_part=question_part, theme_data=refined_themes)

    # Then map the themes
    list_theme_mappings = data["mapping"]
    import_theme_mappings_for_framework(framework, list_theme_mappings)
