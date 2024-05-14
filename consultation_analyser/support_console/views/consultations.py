from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from consultation_analyser.consultations import models
from consultation_analyser.consultations.dummy_data import create_dummy_data
from consultation_analyser.hosting_environment import HostingEnvironment
from consultation_analyser.pipeline.llm_summariser import NO_SUMMARY_STR, create_llm_summaries_for_consultation
from consultation_analyser.pipeline.processing import run_processing_pipeline


@staff_member_required
def index(request: HttpRequest) -> HttpResponse:
    if request.POST:
        try:
            consultation = create_dummy_data(include_themes=False, number_questions=10)
            user = request.user
            consultation.users.add(user)
            messages.success(request, "A dummy consultation has been generated")
        except RuntimeError as error:
            messages.error(request, error.args[0])
    consultations = models.Consultation.objects.all()
    context = {"consultations": consultations, "development_env": HostingEnvironment.is_development_environment()}
    return render(request, "support_console/all-consultations.html", context=context)


@staff_member_required
def show(request: HttpRequest, consultation_slug: str) -> HttpResponse:
    consultation = models.Consultation.objects.get(slug=consultation_slug)
    try:
        if "topic_modelling" in request.POST:
            # Only import when need it - otherwise slow on start-up
            from consultation_analyser.pipeline.ml_pipeline import save_themes_for_consultation

            save_themes_for_consultation(consultation.id)
            messages.success(request, "Topic modelling has been run for this consultation")
        elif "llm_summarisation" in request.POST:
            create_llm_summaries_for_consultation(consultation)
            messages.success(request, "Summaries have been generated for themes using the LLM")
        elif "generate_themes" in request.POST:
            run_processing_pipeline(consultation)
            messages.success(request, "Themes have been generated for this consultation")
        elif "download_json" in request.POST:
            consultation_json = consultation_to_json(consultation)
            response = HttpResponse(consultation_json, content_type='application/json')
            response['Content-Disposition'] = f"attachment; filename={consultation.slug}.json"

            return response

    except RuntimeError as error:
        messages.error(request, error.args[0])
    themes_for_consultation = models.Theme.objects.filter(question__section__consultation=consultation)
    number_of_themes = themes_for_consultation.count()
    number_of_themes_with_summaries = (
        themes_for_consultation.exclude(summary="").exclude(summary=NO_SUMMARY_STR).count()
    )
    number_of_themes_unable_to_summarise = themes_for_consultation.filter(summary=NO_SUMMARY_STR).count()
    number_of_themes_not_yet_summarised = themes_for_consultation.filter(summary="").count()
    context = {
        "consultation": consultation,
        "number_of_themes": number_of_themes,
        "number_of_themes_with_summaries": number_of_themes_with_summaries,
        "number_of_themes_unable_to_summarise": number_of_themes_unable_to_summarise,
        "number_of_themes_not_yet_summarised": number_of_themes_not_yet_summarised,
    }
    return render(request, "support_console/consultation.html", context=context)
