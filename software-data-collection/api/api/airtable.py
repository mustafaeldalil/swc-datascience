def get_all_records_from_table(at, table_id, fields=None, filter_by_formula=None):
    offset = None
    is_fetching = True
    companies = []

    while is_fetching:
        airtable_response = at.get(
            table_id,
            offset=offset,
            fields=fields,
            filter_by_formula=filter_by_formula
        )
        companies += airtable_response["records"]
        offset = airtable_response.get("offset")
        is_fetching = offset is not None

    return companies
