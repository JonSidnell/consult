import pytest
from waffle.testutils import override_switch

from tests.factories import ConsultationFactory


@pytest.mark.django_db
@override_switch("CONSULTATION_PROCESSING", True)
def test_consultation_page(django_app):
    consultation = ConsultationFactory(with_question=True)
    question = consultation.section_set.first().question_set.first()
    homepage = django_app.get("/consultations")
    question_page = homepage.click("Question summary")

    assert "Question summary" in question_page
    assert f"{question.text}" in question_page
