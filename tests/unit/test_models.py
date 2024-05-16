import datetime

import pytest
from django.core.exceptions import ValidationError

from consultation_analyser import factories
from consultation_analyser.consultations import models


@pytest.mark.parametrize("input_keywords,is_outlier", [(["key", "lock"], False), (["dog", "cat"], True)])
@pytest.mark.django_db
def test_save_theme_to_answer(input_keywords, is_outlier):
    question = factories.QuestionFactory(has_free_text=True)
    answer = factories.AnswerFactory(question=question, theme=None)
    # Check theme created and saved to answer
    answer.save_theme_to_answer(keywords=input_keywords, is_outlier=is_outlier)
    theme = models.Theme.objects.get(keywords=input_keywords)
    assert theme.keywords == input_keywords
    assert theme.is_outlier == is_outlier
    assert answer.theme.keywords == input_keywords
    # Check no duplicate created
    answer.save_theme_to_answer(keywords=input_keywords, is_outlier=is_outlier)
    themes_qs = models.Theme.objects.filter(keywords=input_keywords, question=question)
    assert themes_qs.count() == 1


@pytest.mark.django_db
def test_multiple_choice_validation():
    a = factories.AnswerFactory()

    a.multiple_choice = {"totally": "invalid"}

    with pytest.raises(ValidationError):
        a.full_clean()


@pytest.mark.django_db
def test_find_answer_multiple_choice_response():
    q = factories.QuestionFactory(multiple_choice_questions=[("Do you agree?", ["Yes", "No", "Maybe"])])

    factories.AnswerFactory(question=q, multiple_choice_answers=[("Do you agree?", ["Yes"])])
    factories.AnswerFactory(question=q, multiple_choice_answers=[("Do you agree?", ["No"])])
    factories.AnswerFactory(question=q, multiple_choice_answers=[("Do you agree?", ["No"])])

    result = models.Answer.objects.filter_multiple_choice(question="Not a question", answer="Yes")

    assert not result

    result = models.Answer.objects.filter_multiple_choice(question="Do you agree?", answer="wrong")

    assert not result

    result = models.Answer.objects.filter_multiple_choice(question="Do you agree?", answer="Yes")

    assert result.count() == 1

    result = models.Answer.objects.filter_multiple_choice(question="Do you agree?", answer="No")

    assert result.count() == 2
