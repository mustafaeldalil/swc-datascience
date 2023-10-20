import airtable
from dotenv import load_dotenv
from lxml import html
import os

from s3_utils import load_text_file_from_s3

load_dotenv()


def get_scrapped_webpage_from_urls(urls: list[str]) -> dict:
    """ For each url in urls, find s3 path into airtables, then download it, parse it and return the result 

    Parameters
    ----------
    urls : list[str]
        List of urls

    Returns
    -------
    dict
        List of dict containing the url as the key and the webpage scrapped extracted from s3 as value
    """
    at = airtable.Airtable(os.getenv("AIRTABLE_COMPANY_BASE_ID"), os.getenv("AIRTABLE_TOKEN"))
    airtable_rows = at.get(os.getenv("AIRTABLE_COMPANY_WEBSITE_TABLE_ID"))['records']
    result = {}
    for row in airtable_rows:
        fields = row['fields']
        if 'Website URL' in fields and fields['Website URL'] in urls and "Html s3 path" in fields:
            text = load_text_file_from_s3(fields["Html s3 path"])
            result[fields['Website URL']] = text.decode('utf-8')
    return result 


def extract_text_from_webpage(webpage: str) -> str:
    """ Convert the webpage html into a text containing only data we want using lxml.

    Currently we extract only <meta title> and <meta description> tags and all <h1> and <h2> tags

    Parameters
    ----------  
    webpage : str
        The webpage html
    
    Returns
    -------
    str
        The webpage text
    """
    
    tree = html.fromstring(webpage)
    result = []
    
    for elt in tree.xpath('//title'):
        result.append(elt.text_content())
    for elt in tree.xpath('//meta[@name="title"]'):
        result.append(elt.get('content'))
    for elt in tree.xpath('//meta[@name="description"]'):
        result.append(elt.get('content'))
    for elt in tree.xpath('//h1'):
        result.append(elt.text_content())
    for elt in tree.xpath('//h2'):
        result.append(elt.text_content())
    return " ".join(result)
    

if __name__ == '__main__':
    urls = ['https://www.softwareclub.io/']
    webpages = get_scrapped_webpage_from_urls(urls)
    for url, webpage in webpages.items():
        print(url)
        print(extract_text_from_webpage(webpage))
