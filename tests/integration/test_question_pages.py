import html
import re

import pytest
from waffle.testutils import override_switch

from consultation_analyser.consultations import models
from consultation_analyser.factories import (
    AnswerFactory,
    ConsultationFactory,
    ConsultationResponseFactory,
    QuestionFactory,
    SectionFactory,
    UserFactory,
)
from tests.helpers import sign_in


@pytest.mark.django_db
@override_switch("FRONTEND_USER_LOGIN", True)
def test_get_question_summary_page(django_app):
    user = UserFactory()
    consultation = ConsultationFactory(user=user)
    section = SectionFactory(consultation=consultation)
    question = QuestionFactory(
        section=section, multiple_choice_questions=[("What do you think?", ["Yes", "No", "Maybe"])]
    )
    question = models.Question.objects.filter(section__consultation=consultation).first()

    sign_in(django_app, user.email)

    AnswerFactory(multiple_choice_answers=[("What do you think?", ["Yes"])], question=question)
    AnswerFactory(multiple_choice_answers=[("What do you think?", ["Yes"])], question=question)
    AnswerFactory(multiple_choice_answers=[("What do you think?", ["No"])], question=question)
    AnswerFactory(multiple_choice_answers=[("What do you think?", ["Maybe"])], question=question)

    question_summary_url = (
        f"/consultations/{consultation.slug}/sections/{question.section.slug}/questions/{question.slug}/"
    )

    question_page = django_app.get(question_summary_url)
    page_content = html.unescape(str(question_page.content))

    assert question.text in page_content

    answer = question.answer_set.first()
    assert answer.theme.short_description in page_content

    for item in question.multiple_choice_options:
        for opt in item["options"]:
            assert opt in page_content

    for keyword in answer.theme.keywords:
        assert keyword in page_content

    assert re.search(r"Yes\s+50%", question_page.html.text)
    assert re.search(r"No\s+25%", question_page.html.text)
    assert re.search(r"Maybe\s+25%", question_page.html.text)

    filtered_page = django_app.get(f"{question_summary_url}?opinion=Yes")
    assert re.search(r"Yes\s+100%", filtered_page.html.text)
    assert re.search(r"No\s+0%", filtered_page.html.text)
    assert re.search(r"Maybe\s+0%", filtered_page.html.text)
