import pytest

from consultation_analyser.consultations import models
from consultation_analyser.factories import (
    ExecutionRunFactory,
    FreeTextAnswerFactory,
    FreeTextQuestionPartFactory,
    InitialFrameworkFactory,
    InitialThemeFactory,
    ThemeMappingFactory,
)


@pytest.mark.skip("key error - need to fix")
@pytest.mark.django_db
def test_get_latest_theme_mappings_for_question_part_returns_latest_mappings():
    question_part = FreeTextQuestionPartFactory()
    answer = FreeTextAnswerFactory(question_part=question_part)

    # First theme mapping execution run
    first_framework = InitialFrameworkFactory(question_part=question_part)
    theme1 = InitialThemeFactory(framework=first_framework)
    first_execution_run = ExecutionRunFactory(type=models.ExecutionRun.TaskType.THEME_MAPPING)
    ThemeMappingFactory(answer=answer, theme=theme1, execution_run=first_execution_run)

    # Second theme mapping execution run
    second_framework = InitialFrameworkFactory(question_part=question_part)
    theme2 = InitialThemeFactory(framework=second_framework, name="theme 2")
    theme3 = InitialThemeFactory(framework=second_framework, name="theme 3")
    second_execution_run = ExecutionRunFactory(type=models.ExecutionRun.TaskType.THEME_MAPPING)
    ThemeMappingFactory(answer=answer, theme=theme2, execution_run=second_execution_run)
    ThemeMappingFactory(answer=answer, theme=theme3, execution_run=second_execution_run)

    # Get the latest theme mappings
    latest_mappings = models.ThemeMapping.get_latest_theme_mappings_for_question_part(question_part)
    assert latest_mappings.count() == 2
    assert "theme 2" in latest_mappings.values_list("theme__name", flat=True)
    assert all(mapping.execution_run == second_execution_run for mapping in latest_mappings)


@pytest.mark.django_db
def test_get_latest_theme_mappings_for_question_part_no_mappings():
    question_part = FreeTextQuestionPartFactory()
    latest_mappings = models.ThemeMapping.get_latest_theme_mappings_for_question_part(question_part)
    assert latest_mappings.count() == 0


@pytest.mark.django_db
def test_get_history_of_theme_mappings_for_answer():
    question_part = FreeTextQuestionPartFactory()
    answer1 = FreeTextAnswerFactory(question_part=question_part)
    framework = InitialFrameworkFactory(question_part=question_part)
    theme1 = InitialThemeFactory(framework=framework, name="theme 1")
    theme2 = InitialThemeFactory(framework=framework, name="theme 2")
    theme3 = InitialThemeFactory(framework=framework, name="theme 3")

    # Now map a theme to the Answer
    theme_mapping = ThemeMappingFactory(
        answer=answer1, theme=theme1, reason="Theme 1 is most reasonable"
    )

    # Now change the theme mapping
    theme_mapping.theme = theme2
    theme_mapping.save()
    theme_mapping.theme = theme3
    theme_mapping.save()

    # Check current status i.e. latest theme mapping
    assert theme_mapping.theme == theme3
