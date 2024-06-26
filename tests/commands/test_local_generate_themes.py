import json

import pytest
from django.conf import settings
from django.core.management import call_command

from consultation_analyser.consultations.public_schema import ConsultationWithResponsesAndThemes
from consultation_analyser.factories import UserFactory


@pytest.mark.django_db
def test_local_generate_themes(tmp_path):
    UserFactory(email="email@example.com")

    file_path = settings.BASE_DIR / "tests" / "examples" / "chocolate.json"

    call_command("generate_themes", input=file_path, embedding_model="fake", output_dir=tmp_path)

    json_with_themes_path = tmp_path / "consultation_with_themes.json"

    with_themes = json.loads(open(json_with_themes_path).read())

    # Bail if it's invalid
    ConsultationWithResponsesAndThemes(**with_themes)


@pytest.mark.django_db
def test_generate_themes_clean(tmp_path):
    UserFactory(email="email@example.com")

    file_path = settings.BASE_DIR / "tests" / "examples" / "chocolate.json"

    # should not throw
    call_command(
        "generate_themes", input=file_path, embedding_model="fake", clean=True, output_dir=tmp_path
    )

    # we're OK if we make it this far
    assert True
