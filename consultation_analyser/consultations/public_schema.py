# generated by datamodel-codegen:
#   filename:  public_schema.yaml
#   timestamp: 2024-05-03T15:08:40+00:00

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Extra, Field


class Question(BaseModel):
    """
    Questions can be free text, multiple choice or both. The presence of multiple_choice_options implies that the question has a multiple choice part.

    """

    id: UUID = Field(..., description="The ID of this question")
    text: str = Field(
        ...,
        description="The question text",
        examples=[
            "Should it happen on Tuesdays?",
            "Should it happen in the month of May?",
            "Should it happen on a full moon?",
            "Should it happen on Fridays?",
            "Should it be forbidden on Sunday?",
        ],
    )
    has_free_text: bool = Field(..., description="Does this question have a free text component?")
    multiple_choice_options: Optional[List[str]] = Field(
        None,
        description="The options for the multiple choice part of this question, if it has a multiple choice component",
        examples=[["Yes", "No", "I don't know"]],
    )


class Answer(BaseModel):
    """
    Each Answer is associated with a Question and belongs to a ConsultationResponse.
    """

    question_id: UUID = Field(..., description="The ID of the question")
    multiple_choice: Optional[List[str]] = Field(
        None,
        description="Responses to the multiple choice part of the question, if any",
        examples=[["No"]],
    )
    free_text: str = Field(
        ...,
        description="The answer to the free text part of the question, if any",
        examples=[
            "I don't think this is a good idea at all",
            "I would like to point out a few things",
            "I would like clarification on a few key points",
        ],
    )


class ConsultationResponse(BaseModel):
    """
    A ConsultationResponse groups answers. For now it is also a placeholder for response-level information such as demographics, responding-in-the-capacity-of, etc.
    """

    id: UUID = Field(..., description="The ID of the response")
    submitted_at: datetime = Field(..., description="The submission date and time of the response")
    answers: List[Answer] = Field(..., description="The answers in this response", min_items=1)


class Section(BaseModel):
    """
    A Section contains a group of Questions. Consultations that do not have multiple sections should group all Questions under a single Section.
    """

    id: UUID = Field(..., description="The ID of the section")
    name: str = Field(
        ...,
        description="The name of the section",
        examples=[
            "When to enforce a Kit Kat ban",
            "When to encourage the eating of Kit Kats",
            "When Kit Kats are consumed",
        ],
    )
    questions: List[Question] = Field(..., description="The questions in the consultation", min_items=1)


class Consultation(BaseModel):
    """
    Consultation is the top-level object describing a consultation. It contains one or more Sections, which in turn contain Questions.
    """

    class Config:
        extra = Extra.forbid

    name: str = Field(
        ...,
        description="The name of the consultation",
        examples=[
            "Consultation on Kit Kats",
            "How should Kit Kats change",
            "What shall we do about Kit Kats",
        ],
    )
    sections: List[Section] = Field(..., description="The sections of the consultation", min_items=1)


class ConsultationWithResponses(BaseModel):
    """
    A Consultation and its ConsultationResponses
    """

    consultation: Consultation = Field(..., description="The consultation")
    consultation_responses: List[ConsultationResponse] = Field(..., description="The responses", min_items=1)
