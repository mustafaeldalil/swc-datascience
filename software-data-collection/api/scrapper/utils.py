import time
from selenium.webdriver.common.by import By
from urllib.parse import urlparse



def scrap_website(driver, main_url: str, nb_pages_to_scrap: int, page_urls_to_scrap: list, urls_to_exclude: list = []):
    """Scrap a website and return the content of the page.

    Parameters
    ----------
    driver : selenium.webdriver
        Selenium driver.
    main_url : str
        Url of the website to scrap.
    nb_pages_to_scrap : int
        Number of pages to scrap.
    page_url_to_scrap : list
        List of pages to scrap.

    Returns
    -------
    page_sources : list
        List of tuples (url, page_source).
    """
    domain = urlparse(main_url).netloc

    driver.get(main_url)
    time.sleep(2)
    page_sources = []
    page_sources.append((main_url, driver.page_source))

    # Get through all <a> tags
    links = driver.find_elements(By.XPATH, "//a")
    urls_to_add = []
    
    # Add urls when page_url_to_scrap in url
    for link in links:
        url = link.get_attribute("href")
        if url in urls_to_exclude:
            continue

        if url and url not in urls_to_add and any([page_url in url for page_url in page_urls_to_scrap]):
            # Verify if it's a url with same domain
            if urlparse(url).netloc == domain:
                urls_to_add.append(url)
    
    # Complete the urls by first links until nb_pages_to_scrap
    for i, link in enumerate(links):
        if len(urls_to_add) >= nb_pages_to_scrap:
            break
        url = link.get_attribute("href")
        if url in urls_to_exclude:
            continue
        if not url or url in main_url or urlparse(url).netloc != domain:
            continue
        if url not in urls_to_add:
            urls_to_add.append(url)

    # Scrap all urls and add to page_sources
    for url in urls_to_add:
        driver.get(url)
        time.sleep(2)
        page_sources.append((url, driver.page_source))

    return page_sources