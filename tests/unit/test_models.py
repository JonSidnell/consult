import pytest

from consultation_analyser.consultations import models
from tests import factories


@pytest.mark.django_db
def test_save_theme_to_answer():
    question = factories.QuestionFactory(has_free_text=True)
    answer = factories.AnswerFactory(question=question, theme=None)
    keywords = ["key", "lock"]
    label = "0_key_lock"
    # Check theme created and saved to answer
    answer.save_theme_to_answer(theme_label=label, theme_keywords=keywords)
    theme = models.Theme.objects.get(keywords=keywords, label=label)
    assert theme.keywords == keywords
    assert theme.label == label
    assert answer.theme.label == label
    # Check no duplicate created
    answer.save_theme_to_answer(theme_label=label, theme_keywords=keywords)
    themes_qs = models.Theme.objects.filter(keywords=keywords, label=label)
    assert themes_qs.count() == 1


@pytest.mark.django_db
def test_multiple_choice_response_count():
    question = factories.QuestionFactory(multiple_choice_options=["Yes", "No", "Maybe"])
    answers = [
        ["Yes"],
        ["Yes"],
        ["No"],
        ["Maybe"],
        ["No"],
    ]

    for answer in answers:
        factories.AnswerFactory(question=question, multiple_choice_responses=answer)

    response_count = question.multiple_choice_response_counts()

    assert response_count["Yes"].count == 2
    assert response_count["Yes"].percent == 40.0

    assert response_count["No"].count == 2
    assert response_count["No"].percent == 40.0

    assert response_count["Maybe"].count == 1
    assert response_count["Maybe"].percent == 20.0
