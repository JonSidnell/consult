import csv
import datetime
import logging
import os
from io import StringIO

import boto3
from django.conf import settings
from django_rq import job

from consultation_analyser.consultations.models import (
    Answer,
    Consultation,
    QuestionPart,
    ThemeMapping,
)


logger = logging.getLogger("export")


def get_timestamp() -> str:
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d-%H%M%S")


@job("default")
def export_user_theme(consultation_slug: str, s3_key: str) -> None:
    logger.info(f"Starting export for consultation: {consultation_slug}")
    consultation = Consultation.objects.get(slug=consultation_slug)
    output = []

    for question_part in QuestionPart.objects.filter(
        question__consultation=consultation,
        type=QuestionPart.QuestionType.FREE_TEXT,
    ):
        question = question_part.question
        for response in Answer.objects.filter(question_part=question_part):
            original_themes = (
                ThemeMapping.history.filter(answer=response)
                .filter(user_audited=False)
                .filter(history_type="+")
            )
            current_themes = ThemeMapping.objects.filter(answer=response).filter(user_audited=True)
            auditors = set(
                [
                    r.history_user.email
                    for r in response.history.filter(is_theme_mapping_audited=True)
                ]
            )
            output.append(
                {
                    "Consultation": consultation.title,
                    "Question number": question.number,
                    "Question text": question.text,
                    "Question part text": question_part.text,
                    "Response text": response.text,
                    "Response has been audited": response.is_theme_mapping_audited,
                    "Original themes": ", ".join(
                        sorted(
                            [
                                theme_mapping.theme.get_identifier()
                                for theme_mapping in original_themes
                            ]
                        )
                    ),
                    "Current themes": ", ".join(
                        sorted(
                            [
                                theme_mapping.theme.get_identifier()
                                for theme_mapping in current_themes
                            ]
                        )
                    ),
                    "Auditors": ", ".join(list(auditors)),
                    "First audited at": response.datetime_theme_mapping_audited,  # First time audited
                }
            )

    timestamp = get_timestamp()

    if settings.ENVIRONMENT == "local":
        if not os.path.exists("downloads"):
            os.makedirs("downloads")
        with open(
            f"downloads/{timestamp}_example_consultation_theme_changes.csv", mode="w"
        ) as file:
            writer = csv.DictWriter(file, fieldnames=output[0].keys())
            writer.writeheader()
            for row in output:
                writer.writerow(row)
    else:
        if len(s3_key) == 0:
            raise ValueError("s3_key cannot be empty")

        s3_client = boto3.client("s3")

        csv_buffer = StringIO()
        writer = csv.DictWriter(csv_buffer, fieldnames=output[0].keys())
        writer.writeheader()
        for row in output:
            writer.writerow(row)

        s3_client.put_object(
            Bucket=settings.AWS_BUCKET_NAME,
            Key=f"{s3_key}/{timestamp}consultation_theme_changes.csv",
            Body=csv_buffer.getvalue(),
        )
        csv_buffer.close()
    logger.info(f"Finishing export for consultation: {consultation_slug}")
