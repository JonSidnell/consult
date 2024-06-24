import pytest

from consultation_analyser import factories
from consultation_analyser.consultations import models
from consultation_analyser.pipeline.backends.bertopic import BERTopicBackend
from consultation_analyser.pipeline.backends.dummy_topic_backend import DummyTopicBackend
from consultation_analyser.pipeline.ml_pipeline import (
    save_themes_for_consultation,
)


@pytest.mark.django_db
def test_topic_model_end_to_end(tmp_path):
    consultation = factories.ConsultationFactory(name="My new consultation")
    section = factories.SectionFactory(name="Base section", consultation=consultation)
    q = factories.QuestionFactory(has_free_text=True, text="Do you like wolves?", section=section)
    processing_run = factories.ProcessingRunFactory(consultation=consultation)

    # identical answers
    for r in range(10):
        response = factories.ConsultationResponseFactory(consultation=consultation)
        factories.AnswerFactory(
            question=q,
            consultation_response=response,
            free_text="I love wolves, they are fluffy and cute",
        )
    assert models.Theme.objects.count() == 0
    backend = BERTopicBackend()
    save_themes_for_consultation(consultation.id, backend, processing_run)

    # all answers should get the same theme
    assert models.Theme.objects.count() == 1


@pytest.mark.django_db
def test_save_themes_for_consultation():
    consultation = factories.ConsultationFactory(name="My new consultation")
    section = factories.SectionFactory(name="Base section", consultation=consultation)
    processing_run = factories.ProcessingRunFactory(consultation=consultation)
    free_text_question1 = factories.QuestionFactory(
        section=section, has_free_text=True, slug="mars-bar-recipe-change"
    )
    free_text_question2 = factories.QuestionFactory(
        section=section, has_free_text=True, slug="is-crunchie-too-sweet"
    )
    no_free_text_question = factories.QuestionFactory(
        section=section, has_free_text=False, slug="favorite-cadbury-chocolate-bar"
    )
    questions = [free_text_question1, free_text_question2, no_free_text_question]
    for r in range(10):
        response = factories.ConsultationResponseFactory(consultation=consultation)
        [factories.AnswerFactory(question=q, consultation_response=response) for q in questions]

    save_themes_for_consultation(consultation.id, DummyTopicBackend(), processing_run)

    # Check we've generated themes for questions with full text responses, and check fields populated
    for q in [free_text_question1, free_text_question2]:
        themes_for_q = models.Theme.objects.filter(topic_model_metadata__question=q)
        assert themes_for_q.exists()
    example_theme = themes_for_q.first()
    assert example_theme.topic_keywords
    # Summary not populated here - done in a separate step

    # Check no themes for question with no free text
    themes_for_q = models.Theme.objects.filter(topic_model_metadata__question=no_free_text_question)
    assert not themes_for_q.exists()
