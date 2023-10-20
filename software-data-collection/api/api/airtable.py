
def get_all_records_from_table(at, table_id, filter_by_formula=None):

    offset = None
    is_fetching = True

    companies = []
    while is_fetching:
        airtable_response = at.get(
            table_id,
            offset=offset,
            filter_by_formula=filter_by_formula
        )
        companies += airtable_response["records"]
        if "offset" in airtable_response:
            offset = airtable_response["offset"]
        else:
            is_fetching = False
    return companies