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
