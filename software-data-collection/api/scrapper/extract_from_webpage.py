from lxml import html


def _extract_text_from_body(webpage):
    tree_for_body = html.fromstring(webpage)

    bad_tags = [
        "script",
        "style",
        "img",
        "header",
        "nav",
        "noscript",
        "footer",
        "iframe",
        "form",
        "input",
        "button",
    ]

    for tag in bad_tags:
        elements = tree_for_body.xpath(f"//{tag}")
        for element in elements:
            element.getparent().remove(element)

    body = tree_for_body.xpath("//body")[0]
    return body.text_content()


def extract_text_from_webpage(webpage: str, items_to_extract: list) -> str:
    """Convert the webpage html into a text containing only data we want using lxml.

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

    if "title" in items_to_extract:
        for elt in tree.xpath("//title"):
            result.append(elt.text_content())

    if "meta - title" in items_to_extract:
        for elt in tree.xpath('//meta[@name="title"]'):
            result.append(elt.get("content"))

    if "meta - description" in items_to_extract:
        for elt in tree.xpath('//meta[@name="description"]'):
            result.append(elt.get("content"))

    if "body" in items_to_extract:
        result.append(_extract_text_from_body(webpage))
    else:
        for title_balise in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            if title_balise in items_to_extract:
                for elt in tree.xpath(f"//{title_balise}"):
                    result.append(elt.text_content())
    return " ".join(result)



def extract_text_from_webpag_splitted_by_tag(webpage: str, items_to_extract: list) -> str:
    """Convert the webpage html into a text containing only data we want using lxml.

    Currently we extract only <meta title> and <meta description> tags and all <h1> and <h2> tags

    Parameters
    ----------
    webpage : str
        The webpage html

    Returns
    -------
    dict
        dictionary holding text at each tag
    """

    tree = html.fromstring(webpage)
    result = {'title': '', 'description': '', 'body': '', 'h1': '', "h2": '', 'h3': '', 'h4': ''}

    if "title" in items_to_extract:
        for elt in tree.xpath("//title"):
            #result.append('Found in Title: ')
            result["title"] += elt.text_content()
            #result.append(elt.text_content())

    if "meta - title" in items_to_extract:
        for elt in tree.xpath('//meta[@name="title"]'):
            result["title"] += elt.get("content")


    if "meta - description" in items_to_extract:
         
        for elt in tree.xpath('//meta[@name="description"]'):
            result["description"] += elt.get("content")

    if "body" in items_to_extract:
        result["body"] += _extract_text_from_body(webpage)
        
    if "h1" in items_to_extract:
        for elt in  tree.xpath("//h1"):
            result['h1'] += '' if elt.text_content() is None else elt.text_content() 
            
    if "h2" in items_to_extract:
        for elt in  tree.xpath("//h2"):
            result['h2'] +=  '' if elt.text_content() is None else elt.text_content()
    
    if "h3" in items_to_extract:
        for elt in  tree.xpath("//h3"):
            result['h3'] += '' if elt.text_content() is None else elt.text_content()
    
    if "h4" in items_to_extract:
        for elt in  tree.xpath("//h4"):
            result['h4'] += '' if elt.text_content() is None else elt.text_content()
    if "a" in items_to_extract:
        for elt in tree.xpath('//a'):
            result['a'] = '' if elt.get('href') is None else elt.get('href')
            
    return result

