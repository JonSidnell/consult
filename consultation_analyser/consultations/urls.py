from django.urls import include, path
from magic_link import urls as magic_link_urls

from .views import consultations, pages, questions, responses, root, schema, sessions
from .tasks import get_job_status

urlpatterns = [ 
    path("", root.root),
    path("how-it-works/", pages.how_it_works),
    path("schema/", schema.show),
    path("data-sharing/", pages.data_sharing),
    path("get-involved/", pages.get_involved),
    path("privacy/", pages.privacy),
    path("consultations/", consultations.index, name="consultations"),
    path("consultations/new/", consultations.new, name="new_consultation"),
    path("consultations/<str:consultation_slug>/", consultations.show, name="consultation"),
    path("schema/<str:schema_name>.json", schema.raw_schema),
    path(
        "consultations/<str:consultation_slug>/sections/<str:section_slug>/questions/<str:question_slug>/",
        questions.show,
        name="show_question",
    ),
    path(
        "consultations/<str:consultation_slug>/sections/<str:section_slug>/responses/<str:question_slug>/",
        responses.index,
        name="question_responses",
    ),
    # authentication
    path("sign-in/", sessions.new),
    path("sign-out/", sessions.destroy),
    path("magic-link/", include(magic_link_urls)),
    path('django-rq/', include('django_rq.urls')),
    path('consultations/job-status/<str:job_id>/', get_job_status, name='job_status'),
]
