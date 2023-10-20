from api.airtable import get_all_records_from_table
import airtable
from django.conf import settings
import pandas as pd
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from api.s3_utils import save_text_file_to_s3, load_text_file_from_s3
from scrapper.extract_from_webpage import extract_text_from_webpage, extract_text_from_webpag_splitted_by_tag
from ai.nlp import text_processing
import datetime



def get_data_in_airtable_to_csv():
    
    '''Saves data currently in airtable R&D table to csv in current directory'''
    at = airtable.Airtable(settings.AIRTABLE_COMPANY_BASE_ID, settings.AIRTABLE_TOKEN)
    airtable_companies_to_evaluate = get_all_records_from_table(
        at, 
        settings.AIRTABLE_COMPANY_WEBSITE_TABLE_ID, 
        fields= ['Name', 'Last scrapping date', 'Website URL', 'category', 'main category', 'Text provided to GPT', 'Html s3 path', 'category_question_value', 'main_category_question_value', 'category_last_answer_date', 'main_category_last_answer_date']
    )
     # Create a timestamp string
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Create a unique filename using the timestamp string
    filename = f"data_{timestamp_str}"

    # Save the DataFrame to a CSV file wit
    a_df = pd.DataFrame([record['fields'] for record in airtable_companies_to_evaluate])
    a_df.to_csv(f'{filename}.csv')
    
    
# Function to detect language
def detect_language(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False
    
def get_html_code_from_s3(df, items_to_extract = ["title",  "meta - title", "meta - description", "body" , "h1", "h2", "h3", "h4"] ):
        
    '''
    Input: df containing HTML s3 Path
    
    Output: df containing content cleaned
    
    
    '''
    for index, content in df['Html s3 path'].items():
        for company_s3_path in content.split(";"):
            try:
                source_page = load_text_file_from_s3(company_s3_path)
                webpage_text_extracted = extract_text_from_webpage(source_page, items_to_extract)
                df.loc[index, 'content'] += text_processing(webpage_text_extracted)
            except: 
                continue
    return df

   
    
    
def get_html_code_from_s3_by_tag(df, items_to_extract = ["title",  "meta - title", "meta - description", "body" , "h1", "h2", "h3", "h4"] ):
    
    '''
    Input: df containing HTML s3 Path
    
    Output: df containing content cleaned at each tag
    
    
    '''
    for index, content in df['Html s3 path'].items():
        for company_s3_path in content.split(";"):
            try:
                source_page = load_text_file_from_s3(company_s3_path)
                webpage_text_extracted = extract_text_from_webpag_splitted_by_tag(source_page, items_to_extract)
                df.loc[index, 'content_title'] += text_processing(webpage_text_extracted["title"])
                df.loc[index, 'content_description'] += text_processing(webpage_text_extracted["description"])
                df.loc[index, 'content_body'] += text_processing(webpage_text_extracted["body"])
                df.loc[index, 'content_h1'] += text_processing(webpage_text_extracted['h1'])
                df.loc[index, 'content_h2'] += text_processing(webpage_text_extracted['h2'])
                df.loc[index, 'content_h3'] += text_processing(webpage_text_extracted['h3'])
                df.loc[index, 'content_h4'] += text_processing(webpage_text_extracted['h4'])
            except: 
                continue
    return df