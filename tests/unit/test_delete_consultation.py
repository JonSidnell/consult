import pytest

from consultation_analyser.consultations import models
from consultation_analyser import factories


@pytest.mark.django_db
def test_delete_consultation():
    consultation = factories.ConsultationFactory()
    question = factories.QuestionFactory(consultation=consultation)
    question_part = factories.QuestionPartFactory(question=question)
    respondent = factories.RespondentFactory(consultation=consultation)
    factories.AnswerFactory(question_part=question_part, respondent=respondent)


    assert models.Consultation.objects.count() == 1
    assert models.Respondent.objects.count() >= 1
    assert models.Question.objects.count() >= 1
    assert models.QuestionPart.objects.count() >= 1
    assert models.Answer.objects.count() >= 1

    consultation.delete()

    assert models.Consultation.objects.count() == 0
    assert models.Respondent.objects.count() == 0
    assert models.QuestionPart.objects.count() == 0
    assert models.Answer.objects.count() == 0

