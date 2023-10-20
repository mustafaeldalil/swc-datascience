from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from user import views

urlpatterns = [
    path(
        "webhook/sync-profiles-linkedin-results/",
        views.sync_profiles_linkedin_results,
        name="sync-profiles-linkedin-results",
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
