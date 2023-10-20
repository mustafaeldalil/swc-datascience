import re
import spacy 


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

def clean_word(word):
    # If the word has the pattern letter-number-letter, return it as it is
    if re.fullmatch('[a-zA-Z0-9]*[a-zA-Z][0-9]+[a-zA-Z][a-zA-Z0-9]*', word):
        return word
    # Otherwise, remove all non-alphabet, non-space, non-hyphen characters (including numbers)
    else:
        return re.sub('[^a-zA-Z \'-]', '', word)    #TODO remove "-"? replace by " "?
    
    
def text_processing(text):
    """
    Process the raw text extracted from the website to prepare it
    for analysis and translate it in english if necessary
    :param text: Any text in a String format (can be very large)
    :param stopwords: List of english stopwords to be removed from the raw text
    :param nlp: natural language processor
    :return: Clean text ready for analysis
    """
    with open('stopwords_.txt', 'r') as f:
        stopwords = f.read().splitlines()


    # Clean the text by removing numbers, special characters and stopwords
    text = text.lower()
    text = text.replace("\n", " ")  # Try to use text.strip()
    text = ' '.join(clean_word(word) for word in text.split())
    text = ' '.join(word for word in text.split() if word not in stopwords)


    return text

def remove_dates_and_persons(text):
    # Process the text
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Analyze syntax
    filtered_sentences = []
    for sent in doc.sents:
        filtered_entities = [entity for entity in sent.ents if entity.label_ not in ['DATE', 'PERSON']]
        anonymous_sentence = str(sent)
        for entity in filtered_entities:
            anonymous_sentence = anonymous_sentence.replace(entity.text, "")
        filtered_sentences.append(anonymous_sentence)

    # Join the sentences back together
    filtered_text = " ".join(filtered_sentences)
    return filtered_text