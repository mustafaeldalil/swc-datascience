import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

app = Celery("api")
app.config_from_object("django.conf:settings")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.task_routes = {
    "company.tasks.sync_companies_to_gsheet": {"queue": "software_default"},
    'company.tasks.sync_companiy_employees_to_gsheet': {'queue': 'software_default'},
    "company.tasks.planify_scrap_companies_website": {"queue": "software_default"},
    "company.tasks.planify_answer_questions": {"queue": "software_default"},
    "company.tasks.scrap_company_website": {"queue": "software_slow"},
    "company.tasks.answer_question": {"queue": "software_slow"},
    "user.tasks.sync_linkedin_user_profiles_to_gsheet": {"queue": "software_default"},
}

app.conf.beat_schedule = {
    "planify-answer-questions": {
        "task": "company.tasks.planify_answer_questions",
        "schedule": crontab(day_of_week="*", hour="*", minute="31"),
    },
    "planify-scrap-companies-website": {
        "task": "company.tasks.planify_scrap_companies_website",
        "schedule": crontab(day_of_week="*", hour="*", minute="45"),
    },
    "synchronize-companies-to-gsheet": {
        "task": "company.tasks.sync_companies_to_gsheet",
        "schedule": crontab(day_of_week="*", hour="*", minute="12"),
    },
    "synchronize-linkedin-profiles-to-gsheet": {
        "task": "user.tasks.sync_linkedin_user_profiles_to_gsheet",
        "schedule": crontab(day_of_week="*", hour="*", minute="20"),
    },
}
