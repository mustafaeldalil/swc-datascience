from django.conf import settings
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def read_from_gsheet(filename, tab_number):
    # define the scope
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        settings.GOOGLE_API_KEY_JSON_NAME, scope
    )

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open(filename)

    # get all the sheets in the Spreadsheet
    sheet_instance = sheet.get_worksheet(tab_number)

    return sheet_instance.get_all_records()


def add_row_on_gsheet(filename, tab_number, rows):
    # define the scope
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        settings.GOOGLE_API_KEY_JSON_NAME, scope
    )

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open(filename)

    # get all the sheets in the Spreadsheet
    sheet_instance = sheet.get_worksheet(tab_number)

    sheet_instance.append_rows(rows)


def delete_rows_on_gsheet(filename: str, tab_number: int, airtable_ids: set):
    # define the scope
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]

    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        settings.GOOGLE_API_KEY_JSON_NAME, scope
    )

    # authorize the clientsheet
    client = gspread.authorize(creds)

    # get the instance of the Spreadsheet
    sheet = client.open(filename)

    # get all the sheets in the Spreadsheet
    sheet_instance = sheet.get_worksheet(tab_number)

    rows = sheet_instance.get_all_records()
    nb_delete = 0
    for index, row in enumerate(rows):
        if row["airtable_id"] in airtable_ids:
            sheet_instance.delete_row(index + 2 - nb_delete)
            nb_delete += 1
