import airtable
import datetime
import json
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from company.google_utils import delete_rows_on_gsheet, read_from_gsheet
from company.constants import LINKEDIN_COMPANIES_FIELDS_MAPPING, LINKEDIN_COMPANY_EMPLOYEES_FIELDS_MAPPING


def _map_fields_to_linkedin_companies_fields(row):
    return {
        LINKEDIN_COMPANIES_FIELDS_MAPPING[key]: value
        for key, value in row.items()
        if key in LINKEDIN_COMPANIES_FIELDS_MAPPING
    }


def _map_fields_to_linkedin_company_employees_fields(row):
    return {
        LINKEDIN_COMPANY_EMPLOYEES_FIELDS_MAPPING[key]: value
        for key, value in row.items()
        if key in LINKEDIN_COMPANY_EMPLOYEES_FIELDS_MAPPING
    }
 

@api_view(["POST"])
def sync_companies_linkedin_results(request):
    if not request.data.get("resultObject"):
        return Response({"status": "error", "message": "Missing resultObject"})
    results = json.loads(request.data["resultObject"])
    input_rows = read_from_gsheet(
        filename=settings.GOOGLE_COMPANY_TO_SCRAP_LINKEDIN_SHEET_FILENAME, tab_number=0
    )
    url_ids = {row["linkedin_url"]: row["airtable_id"] for row in input_rows}
    at = airtable.Airtable(settings.AIRTABLE_COMPANY_BASE_ID, settings.AIRTABLE_TOKEN)
    airtable_ids_to_delete_from_gsheet = []
    for result in results:
        airtable_id = url_ids[result["query"]]

        data = {
            "company": [url_ids[result["query"]]],
            "Scrapping date": str(datetime.datetime.now()),
            **_map_fields_to_linkedin_companies_fields(result),
        }
        at.create(settings.AIRTABLE_COMPANY_LINKEDIN_RESULT_ID, data)
        at.update(
            settings.AIRTABLE_COMPANY_LINKEDIN_TABLE_ID,
            airtable_id,
            {
                "Scrapping ongoing": "No",
                "Last scrapping date": str(datetime.datetime.now()),
            },
        )
        airtable_ids_to_delete_from_gsheet.append(airtable_id)

    delete_rows_on_gsheet(
        filename=settings.GOOGLE_COMPANY_TO_SCRAP_LINKEDIN_SHEET_FILENAME,
        tab_number=0,
        airtable_ids=airtable_ids_to_delete_from_gsheet,
    )
    return Response({"status": "ok"})


@api_view(["POST"])
def sync_company_employees_linkedin_results(request):
    if not request.data.get("resultObject"):
        return Response({"status": "error", "message": "Missing resultObject"})
    results = json.loads(request.data["resultObject"])
    input_rows = read_from_gsheet(
        filename=settings.GOOGLE_COMPANY_EMPLOYEES_TO_SCRAP_LINKEDIN_SHEET_FILENAME, tab_number=0
    )
    url_ids = {row["url"]: row["airtable_id"] for row in input_rows}
    at = airtable.Airtable(settings.AIRTABLE_COMPANY_BASE_ID, settings.AIRTABLE_TOKEN)
    airtable_ids_to_delete_from_gsheet = []
    for result in results:
        airtable_id = url_ids[result["query"]]

        data = {
            "Company URL": result["query"],
            "company": [url_ids[result["query"]]],
            "Scrapping date": str(datetime.datetime.now()),
            **_map_fields_to_linkedin_company_employees_fields(result),
        }
        at.create(settings.AIRTABLE_COMPANY_EMPLOYEES_LINKEDIN_RESULT_ID, data)
        at.update(
            settings.AIRTABLE_COMPANY_LINKEDIN_TABLE_ID,
            airtable_id,
            {
                "Employees scrapping ongoing": "No",
                "Last employees scrapping date": str(datetime.datetime.now()),
            },
        )
        airtable_ids_to_delete_from_gsheet.append(airtable_id)

    delete_rows_on_gsheet(
        filename=settings.GOOGLE_COMPANY_EMPLOYEES_TO_SCRAP_LINKEDIN_SHEET_FILENAME,
        tab_number=0,
        airtable_ids=airtable_ids_to_delete_from_gsheet,
    )
    return Response({"status": "ok"})