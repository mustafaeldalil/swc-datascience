import airtable
import datetime
import json
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response

from company.google_utils import delete_rows_on_gsheet, read_from_gsheet
from user.constants import (
    LINKEDIN_PROFILE_FIELDS_MAPPING,
    LINKEDIN_PROFILE_GENERAL_FIELDS_MAPPING,
    LINKEDIN_PROFILE_DETAILS_FIELDS_MAPPING,
    LINKEDIN_PROFILE_JOB_FIELDS_MAPPING,
    LINKEDIN_PROFILE_SCHOOL_FIELDS_MAPPING,
)


def _map_fields_to_linkedin_companies_fields(row):
    data = {}
    for key, mapped_value in LINKEDIN_PROFILE_FIELDS_MAPPING.items():
        if key in row.keys():
            data[mapped_value] = row[key]
    if "general" in row.keys():
        for key, mapped_value in LINKEDIN_PROFILE_GENERAL_FIELDS_MAPPING.items():
            if key in row["general"].keys():
                data[mapped_value] = row["general"][key]
    if "details" in row.keys():
        for key, mapped_value in LINKEDIN_PROFILE_DETAILS_FIELDS_MAPPING.items():
            if key in row["details"].keys():
                data[mapped_value] = row["details"][key]
    if "jobs" in row.keys():
        for job_index, job in enumerate(row["jobs"][:3]):
            for key, mapped_value in LINKEDIN_PROFILE_JOB_FIELDS_MAPPING.items():
                if key in job.keys():
                    data[f"job{job_index + 1}_{mapped_value}"] = job[key]
    if "schools" in row.keys():
        for school_index, school in enumerate(row["schools"][:3]):
            for key, mapped_value in LINKEDIN_PROFILE_SCHOOL_FIELDS_MAPPING.items():
                if key in school.keys():
                    data[f"school{school_index + 1}_{mapped_value}"] = school[key]

    return data


@api_view(["POST"])
def sync_profiles_linkedin_results(request):
    if not request.data.get("resultObject"):
        return Response({"status": "error", "message": "Missing resultObject"})
    results = json.loads(request.data["resultObject"])
    input_rows = read_from_gsheet(
        filename=settings.GOOGLE_PROFILE_TO_SCRAP_LINKEDIN_SHEET_FILENAME, tab_number=0
    )
    url_ids = {row["linkedin_url"]: row["airtable_id"] for row in input_rows}
    at = airtable.Airtable(
        settings.AIRTABLE_PROFILE_LINKEDIN_BASE_ID, settings.AIRTABLE_TOKEN
    )
    airtable_ids_to_delete_from_gsheet = []
    for result in results:
        airtable_id = url_ids[result["query"]]

        data = {
            "url": result["query"],
            "profile": [url_ids[result["query"]]],
            "Scrapping date": str(datetime.datetime.now()),
            **_map_fields_to_linkedin_companies_fields(result),
        }
        at.create(settings.AIRTABLE_PROFILE_LINKEDIN_RESULT_ID, data)
        at.update(
            settings.AIRTABLE_PROFILE_LINKEDIN_TABLE_ID,
            airtable_id,
            {
                "Scrapping ongoing": "No",
                "Last scrapping date": str(datetime.datetime.now()),
            },
        )
        airtable_ids_to_delete_from_gsheet.append(airtable_id)

    delete_rows_on_gsheet(
        filename=settings.GOOGLE_PROFILE_TO_SCRAP_LINKEDIN_SHEET_FILENAME,
        tab_number=0,
        airtable_ids=airtable_ids_to_delete_from_gsheet,
    )
    return Response({"status": "ok"})
