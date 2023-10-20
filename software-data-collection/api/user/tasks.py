from django.conf import settings
import airtable
from api.celery import app
from api.airtable import get_all_records_from_table
from company.google_utils import add_row_on_gsheet, read_from_gsheet


PROFILE_EMPLOYEES_TO_SYNC_AIRTABLE_FILTER_BY = """AND(
    {Linkedin URL} != '', 
    {Scrapping ongoing} = 'No',
    OR(
        {Last scrapping date} = '',
        IS_BEFORE({Last scrapping date}, DATEADD(TODAY(), -{Frequency (month)}, 'months'))
    )
)"""


@app.task(bind=True)
def sync_linkedin_user_profiles_to_gsheet(self):

    at = airtable.Airtable(settings.AIRTABLE_PROFILE_LINKEDIN_BASE_ID, settings.AIRTABLE_TOKEN)
    airtable_profiles_to_scrap = get_all_records_from_table(
        at, 
        settings.AIRTABLE_PROFILE_LINKEDIN_TABLE_ID,
        filter_by_formula=PROFILE_EMPLOYEES_TO_SYNC_AIRTABLE_FILTER_BY
    )

    google_companies_rows = read_from_gsheet(
        filename=settings.GOOGLE_PROFILE_TO_SCRAP_LINKEDIN_SHEET_FILENAME, tab_number=0
    )
    airtable_profile_ids = [row["airtable_id"] for row in google_companies_rows]

    # COMPANIES LINKEDIN SCRAPPING
    profiles_to_scrap = []
    for row in airtable_profiles_to_scrap:
        if row["id"] in airtable_profile_ids:
            continue
        fields = row["fields"]
        profiles_to_scrap.append(
            [
                row["id"],
                fields["Linkedin URL"],
            ]
        )
        
    add_row_on_gsheet(
        filename=settings.GOOGLE_PROFILE_TO_SCRAP_LINKEDIN_SHEET_FILENAME,
        tab_number=0,
        rows=profiles_to_scrap,
    )

    for profile in profiles_to_scrap:
        at.update(
            settings.AIRTABLE_PROFILE_LINKEDIN_TABLE_ID,
            profile[0],
            {"Scrapping ongoing": "Yes"},
        )

    return profiles_to_scrap