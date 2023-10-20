from django.conf import settings
import airtable
import datetime
import time
from langdetect import detect
from ai.embedder import Embedder 
from ai.nlp import preprocess, text_to_chunks
from ai.semantic_retrieval import SemanticSimilarityCalculator
from api.airtable import get_all_records_from_table
from api.celery import app
from api.gpt import generate_gpt_answer
from api.s3_utils import save_text_file_to_s3, load_text_file_from_s3
from company.google_utils import add_row_on_gsheet, read_from_gsheet
from scrapper.extract_from_webpage import extract_text_from_webpage
from scrapper.selenium_initialization import initialize_selenium
from scrapper.utils import scrap_website


COMPANIES_TO_SYNC_AIRTABLE_FILTER_BY = """AND(
    {Linkedin URL} != '', 
    {Scrapping ongoing} = 'No',
    OR(
        {Last scrapping date} = '',
        IS_BEFORE({Last scrapping date}, DATEADD(TODAY(), -{Frequency (month)}, 'months'))
    )
)"""

COMPANIES_EMPLOYEES_TO_SYNC_AIRTABLE_FILTER_BY = """AND(
    {Linkedin URL} != '', 
    {Employees scrapping ongoing} = 'No',
    OR(
        {Last employees scrapping date} = '',
        IS_BEFORE({Last employees scrapping date}, DATEADD(TODAY(), -{Frequency (month)}, 'months'))
    )
)"""

COMPANY_WEBSITE_TO_SYNC_AIRTABLE_FILTER_BY = """AND(
    {Website URL} != '', 
    {Scrapped} = 'No'
)"""


def _clean_url(url):
    "Remove all trailing slash and ."
    url = url.strip()
    url = url.replace("/", "_")
    url = url.replace(".", "_")
    return url


@app.task(bind=True)
def sync_companies_to_gsheet(self):
    at = airtable.Airtable(settings.AIRTABLE_COMPANY_BASE_ID, settings.AIRTABLE_TOKEN)
    airtable_companies_to_scrap = get_all_records_from_table(
        at, 
        settings.AIRTABLE_COMPANY_LINKEDIN_TABLE_ID,
        filter_by_formula=COMPANIES_TO_SYNC_AIRTABLE_FILTER_BY
    )

    google_companies_rows = read_from_gsheet(
        filename=settings.GOOGLE_COMPANY_TO_SCRAP_LINKEDIN_SHEET_FILENAME, tab_number=0
    )
    airtable_company_ids = [row["airtable_id"] for row in google_companies_rows]

    # COMPANIES LINKEDIN SCRAPPING
    companies_to_scrap = []
    for row in airtable_companies_to_scrap:
        if row["id"] in airtable_company_ids:
            continue
        fields = row["fields"]
        companies_to_scrap.append(
            [
                row["id"],
                fields["Linkedin URL"],
            ]
        )
        
    add_row_on_gsheet(
        filename=settings.GOOGLE_COMPANY_TO_SCRAP_LINKEDIN_SHEET_FILENAME,
        tab_number=0,
        rows=companies_to_scrap,
    )

    for company in companies_to_scrap:
        at.update(
            settings.AIRTABLE_COMPANY_LINKEDIN_TABLE_ID,
            company[0],
            {"Scrapping ongoing": "Yes"},
        )

    return companies_to_scrap


@app.task(bind=True)
def sync_companiy_employees_to_gsheet(self):
    at = airtable.Airtable(settings.AIRTABLE_COMPANY_BASE_ID, settings.AIRTABLE_TOKEN)
    airtable_companies_to_scrap = get_all_records_from_table(
        at, 
        settings.AIRTABLE_COMPANY_LINKEDIN_TABLE_ID,
        filter_by_formula=COMPANIES_EMPLOYEES_TO_SYNC_AIRTABLE_FILTER_BY
    )

    google_companies_rows = read_from_gsheet(
        filename=settings.GOOGLE_COMPANY_EMPLOYEES_TO_SCRAP_LINKEDIN_SHEET_FILENAME, tab_number=0
    )
    airtable_company_ids = [row["airtable_id"] for row in google_companies_rows]

    # COMPANIES LINKEDIN SCRAPPING
    companies_employees_to_scrap = []
    for row in airtable_companies_to_scrap:
        if row["id"] in airtable_company_ids:
            continue
        fields = row["fields"]
        companies_employees_to_scrap.append(
            [
                row["id"],
                fields["Linkedin URL"],
            ]
        )
        
    add_row_on_gsheet(
        filename=settings.GOOGLE_COMPANY_EMPLOYEES_TO_SCRAP_LINKEDIN_SHEET_FILENAME,
        tab_number=0,
        rows=companies_employees_to_scrap,
    )

    for company in companies_employees_to_scrap:
        at.update(
            settings.AIRTABLE_COMPANY_LINKEDIN_TABLE_ID,
            company[0],
            {"Employees scrapping ongoing": "Yes"},
        )

    return companies_employees_to_scrap


@app.task(bind=True)
def planify_scrap_companies_website(self):
    at = airtable.Airtable(
        settings.AIRTABLE_COMPANY_WEBSITE_BASE_ID, settings.AIRTABLE_TOKEN
    )
    airtable_rows = get_all_records_from_table(
        at, 
        settings.AIRTABLE_COMPANY_WEBSITE_TABLE_ID,
        filter_by_formula=COMPANY_WEBSITE_TO_SYNC_AIRTABLE_FILTER_BY
    ) 
    
    at.get(settings.AIRTABLE_COMPANY_WEBSITE_TABLE_ID)["records"]
    
    companies_to_scrap = []
    for row in airtable_rows:
        fields = row["fields"]
        scrap_company_website.delay({"id": row["id"], "url": fields["Website URL"]})
        companies_to_scrap.append({"id": row["id"], "url": fields["Website URL"]})
    return companies_to_scrap


@app.task(bind=True)
def scrap_company_website(self, company):
    at = airtable.Airtable(
        settings.AIRTABLE_COMPANY_WEBSITE_BASE_ID, settings.AIRTABLE_TOKEN
    )

    # Get parameters of scrapping
    parameter_rows = at.get(settings.AIRTABLE_PAGE_TO_SCRAP_ID)["records"]
    nb_pages_to_scrap = int(parameter_rows[0]["fields"]["Number of pages to scrap"])
    page_urls_to_scrap = []
    urls_to_exclude = []
    for row in parameter_rows:
        fields = row["fields"]
        if "Part of the url" in fields:
            page_urls_to_scrap.append(fields["Part of the url"])
        if "Exclude urls" in fields:
            urls_to_exclude.append(fields["Exclude urls"])

    driver = initialize_selenium()
    print(company['url'])
    if not company['url'].startswith('http'):
        return 

    source_pages = scrap_website(driver, company["url"], nb_pages_to_scrap, page_urls_to_scrap, urls_to_exclude)
    driver.close()
    filenames = []
    urls = []
    for (url, source_page) in source_pages:
        filename = f"{company['id']}/{company['id']}-{_clean_url(url)}.html"
        save_text_file_to_s3(filename, source_page)
        filenames.append(filename)
        urls.append(url)

    # Detect language of main page
    main_page_source_code = source_pages[0][1]
    main_page_titles_text = extract_text_from_webpage(main_page_source_code, ["h1", "h2", "h3", "h4"])
    language = detect(main_page_titles_text)
    at.update(
        settings.AIRTABLE_COMPANY_WEBSITE_TABLE_ID,
        company["id"],
        {
            "Scrapped": "Yes",
            "Last scrapping date": str(datetime.datetime.now()),
            'Urls scrapped': ";".join(urls),
            "Language": language,
            "Html s3 path": ";".join(filenames)
        },
    )

    return company


@app.task(bind=True)
def planify_answer_questions(self):
    at = airtable.Airtable(
        settings.AIRTABLE_COMPANY_WEBSITE_BASE_ID, settings.AIRTABLE_TOKEN
    )

    prompt_context = at.get(settings.AIRTABLE_PROMPT_CONTEXT_ID)["records"][0][
        "fields"
    ]["Context"]

    items_to_extract_rows = at.get(settings.AIRTABLE_PAGE_EXTRACTOR_ID)["records"]
    items_to_extract = []
    for row in items_to_extract_rows:
        try:
            fields = row["fields"]
            if fields["Extract"] == "Yes":
                items_to_extract.append(fields["Type"])
        except Exception as e:
            print(e)
            continue

    airtable_rows = at.get(settings.AIRTABLE_COMPANY_WEBSITE_TABLE_ID)["records"]
    nb_companies = 0
    for row in airtable_rows:
        try:
            company_airtable_id = row["id"]
            fields = row["fields"]
            if fields["AI info extracted"] == "Yes":
                continue

            company_s3_paths = row["fields"]["Html s3 path"]
            answer_question.delay(
                company_airtable_id, company_s3_paths, prompt_context, items_to_extract
            )
            nb_companies += 1
        except Exception as e:
            print(e)
            continue
    return {"companiesSendToGpt": nb_companies}


@app.task(bind=True)
def answer_question(
    self, company_airtable_id, company_s3_paths, prompt_context, items_to_extract
):
    at = airtable.Airtable(
        settings.AIRTABLE_COMPANY_WEBSITE_BASE_ID, settings.AIRTABLE_TOKEN
    )
    questions = at.get(settings.AIRTABLE_QUESTIONS_QUERIES_ID)["records"][0]["fields"]

    content = ""
    for company_s3_path in company_s3_paths.split(";"):
        source_page = load_text_file_from_s3(company_s3_path)
        webpage_text_extracted = extract_text_from_webpage(source_page, items_to_extract)
        content += f"\n\n {webpage_text_extracted}"

    # Embed and chuck the text
    texts = preprocess(content)

    if not texts:
        at.update(
            settings.AIRTABLE_COMPANY_WEBSITE_TABLE_ID,
            company_airtable_id,
            {
                "AI info extracted": "Yes",
                "Text provided to GPT": "TEXT EMPTY",
            },
        )
        return {
            "AI info extracted": "Yes",
            "Text provided to GPT": "TEXT EMPTY",
        }

    chunks = text_to_chunks(texts)
    embedder = Embedder()
    embeddings = embedder.get_text_embedding(chunks)
    chunk_embeddings = []
    for embedding, chunk in zip(embeddings, chunks):
        chunk_embeddings.append({"embedding": embedding.tolist(), "chunk": chunk})

    results = []
    for question_key, question_value in questions.items():
        try:
            # Retrieve the top 5 chunks
            # Embed question
            question_embedding = embedder.get_text_embedding([question_value])

            semantic_calculator = SemanticSimilarityCalculator(chunk_embeddings, n_neighbors=5)

            topn_chunks = semantic_calculator.retrieve_top_chunks(question_embedding)

            prompt = "Chunks of webpage content:\n\n"

            for c in topn_chunks:
                prompt += c + "\n\n"

            prompt += f"\n\n{prompt_context.replace('<QUESTION>', question_value)}"

            answer = generate_gpt_answer(prompt)
            at.update(
                settings.AIRTABLE_COMPANY_WEBSITE_TABLE_ID,
                company_airtable_id,
                {
                    question_key: answer,
                    "AI info extracted": "Yes",
                    "Text provided to GPT": prompt,
                },
            )
            results.append({"question": question_key, "answer": answer})
            time.sleep(2)
        except Exception as e:
            print(e)
            continue
    return results