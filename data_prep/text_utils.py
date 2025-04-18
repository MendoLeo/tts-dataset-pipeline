import re
import unicodedata
import json
import uroman as ur
from norm_confg import norm_config 

def text_normalize(text, iso_code, lower_case=True, remove_numbers=True, remove_brackets=False):

    """Given a text, normalize it by changing to lower case, removing punctuations, removing words that only contain digits and removing extra spaces

    Args:
        text : The string to be normalized
        iso_code :
        remove_numbers : Boolean flag to specify if words containing only digits should be removed

    Returns:
        normalized_text : the string after all normalization  

    """

    config = norm_config.get(iso_code, norm_config["*"])

    for field in ["lower_case", "punc_set","del_set", "mapping", "digit_set", "unicode_norm"]:
        if field not in config:
            config[field] = norm_config["*"][field]


    text = unicodedata.normalize(config["unicode_norm"], text)

    # Convert to lower case

    if config["lower_case"] and lower_case:
        text = text.lower()

    # brackets
    
    # always text inside brackets with numbers in them. Usually corresponds to "(Sam 23:17)"
    text = re.sub(r"\([^\)]*\d[^\)]*\)", " ", text)
    if remove_brackets:
        text = re.sub(r"\([^\)]*\)", " ", text)

    # Apply mappings

    for old, new in config["mapping"].items():
        text = re.sub(old, new, text)

    # Replace punctutations with space

    punct_pattern = r"[" + config["punc_set"]

    punct_pattern += "]"

    normalized_text = re.sub(punct_pattern, " ", text)

    # remove characters in delete list

    delete_patten = r"[" + config["del_set"] + "]"

    normalized_text = re.sub(delete_patten, "", normalized_text)

    # Remove words containing only digits
    # We check for 3 cases  a)text starts with a number b) a number is present somewhere in the middle of the text c) the text ends with a number
    # For each case we use lookaround regex pattern to see if the digit pattern in preceded and followed by whitespaces, only then we replace the numbers with space
    # The lookaround enables overlapping pattern matches to be replaced

    if remove_numbers:

        digits_pattern = "[" + config["digit_set"]

        digits_pattern += "]+"
# add a list of general devise handling as Euro, Fcfa,etc
        complete_digit_pattern = (
            r"^"
            + digits_pattern
            + "(?=\s)|(?<=\s)"
            + digits_pattern
            + "(?=\s)|(?<=\s)"
            + digits_pattern
            + "$"
        )

        normalized_text = re.sub(complete_digit_pattern, "*", normalized_text)

    if config["rm_diacritics"]:
        from unidecode import unidecode
        normalized_text = unidecode(normalized_text)

    # Remove extra spaces
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()

    return normalized_text


def normalize_uroman(text)-> list[str]:
    """
    normalize_uroman _summary_

    Args:
        text (_type_): _description_

    Returns:
        _type_: _description_
    """

    text = text.lower()
    text = re.sub("([^a-z' ])", " ", text)
    text = re.sub(' +', ' ', text)
    return text.strip()

def load_transcripts(json_path, chapter):
    with open(json_path, "r") as f:
        data = json.load(f)
       
    # convert MAT.19.1 -> MAT_019
    get_chapter = lambda x: x.split('.')[0] + '_' + x.split('.')[1].zfill(3)  # noqa: E731
    # filter by book and chapter
    transcripts = [d["verset"] for d in data if get_chapter(d["numVerset"]) == chapter]
    verse_ids = [d["numVerset"] for d in data if get_chapter(d["numVerset"]) == chapter]
    return verse_ids, transcripts

def preprocess_verse(text:str,lang:str):
    special_isos_uroman = "ara, bel, bul, deu, ell, eng, fas, grc, ell, eng, heb, kaz, kir, lav, lit, mkd, mkd2, oss, pnt, pus, rus, srp, srp2, tur, uig, ukr, yid".split(",")
    special_isos_uroman = [i.strip() for i in special_isos_uroman]

    uroman = ur.Uroman()

    if lang in special_isos_uroman:
        romanized_text = uroman.romanize_string(text,lcode=lang)
        norm_text = normalize_uroman(romanized_text)
    else:
        romanized_text = uroman.romanize_string(text)
        norm_text = text_normalize(romanized_text,lang)
    

    return norm_text


def pre_processing(json_path:str,chapter:str,lang:str):

    # load transcript
    verse_ids, transcripts = load_transcripts(json_path, chapter)
    verses= [preprocess_verse(v,lang) for v in transcripts]
    

    augmented_verses = ["*"] * len(verses) * 2
    augmented_verses[1::2] = verses
    words=[verse.split() for verse in transcripts] # initial transcripts without normalization
    stared_words = [word for verse in augmented_verses for word in verse.split()] # stared verses

    return stared_words, words  


