import re


def preprocess(text):
    """Preprocess text
    - Remove newlines
    - Remove extra whitespaces
    """

    text = text.replace("\n", " ")
    text = re.sub(r"\s+", " ", text)
    return text


def text_to_chunks(text: str, word_length: int = 200):
    """Split text into chunks of word_length words

    Parameters
    ----------
    text : str
        The text to split
    word_length : int
        The length of the chunks in words

    Returns
    -------
    list[str]
        The list of chunks
    """
    text_toks = text.split(" ")
    chunks = []

    for i in range(0, len(text_toks), word_length):
        chunk = text_toks[i:min(i + word_length, len(text_toks))]
        chunk = " ".join(chunk).strip()
        chunks.append(chunk)
    return chunks
