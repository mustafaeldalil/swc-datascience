from django.urls import path
from company import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path("webhook/sync-companies-linkedin-results/", views.sync_companies_linkedin_results, name="sync-companies-linkedin-results"),
    path("webhook/sync-company-employees-linkedin-results/", views.sync_company_employees_linkedin_results, name="sync-company-employees-linkedin-results"),

]

urlpatterns = format_suffix_patterns(urlpatterns)
