import re
import emoji
from unidecode import unidecode
from nltk.corpus import stopwords

try:
    from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    SASTRAWI_AVAILABLE = True
except ImportError:
    SASTRAWI_AVAILABLE = False


def replace_slang(text):    
    # 2. Slang dictionary and utility functions
    slang_dict = {
        "gk": "tidak",
        "ga": "tidak",
        "tdk": "tidak",
        "aja": "saja",
        # Add more slang words as needed
    }
    words = text.split()
    return ' '.join([slang_dict.get(w, w) for w in words])

def remove_extra_chars(text):
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    return text

def convert_emojis(text):
    return emoji.demojize(text, delimiters=(" ", " "), language='id')

def remove_usernames(text):
    return re.sub(r'@\w+', '{USER}', text)

def remove_numbers(text):
    return re.sub(r'\d+', '', text)

def remove_punctuation(text):
    return re.sub(r'[^\w\s{}]', ' ', text)

def replace_links(text):
    return re.sub(r'http[s]?://\S+|www\.\S+', '{LINK}', text)

def normalize_text(text):
    # Convert to ASCII, remove unsupported formatting
    return unidecode(str(text))




# Init stemmer
factory = StemmerFactory()
stemmer = factory.create_stemmer()

# List of exceptions (placeholders)
EXCEPTIONS = {"{LINK}", "{USER}"}

def stem_with_exceptions(text):
    tokens = text.split()  # simple tokenization by space
    stemmed_tokens = []
    
    for token in tokens:
        if token in EXCEPTIONS:  
            stemmed_tokens.append(token)  # keep as is
        else:
            stemmed_tokens.append(stemmer.stem(token))
    
    return " ".join(stemmed_tokens)


def preprocess_tfidf(text):
    text_process = convert_emojis(text)
    text_process = normalize_text(text_process)
    text_process = replace_slang(text_process)
    text_process = remove_extra_chars(text_process)
    text_process = text_process.lower()
    text_process = replace_links(text_process)
    text_process = remove_numbers(text_process)
    text_process = remove_punctuation(text_process)
    text_process = stem_with_exceptions(text_process)
    tokens = text_process.split()
    stop_words = set(stopwords.words('indonesian'))
    text_process = ' '.join([w for w in tokens if w.lower() not in stop_words])
    return text_process

def preprocess_bert(text):
    """BERT preprocessing pipeline for transformer models"""
    # Convert emojis
    text = emoji.demojize(text, delimiters=(" ", " "), language='id')
    # Normalize
    text = unidecode(str(text))
    # Remove extra chars
    text = re.sub(r'(.)\1{2,}', r'\1', text)
    # Lowercase
    text = text.lower()
    # Replace links
    text = re.sub(r'http[s]?://\S+|www\.\S+', 'HTTPURL', text)
    # Remove numbers
    text = re.sub(r'\d+', '', text)
    # Remove punctuation
    text = re.sub(r'[^\w\s{}]', ' ', text)
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

