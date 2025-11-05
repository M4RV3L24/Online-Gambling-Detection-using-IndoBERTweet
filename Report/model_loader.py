import joblib
import streamlit as st
from preprocessing import preprocess_tfidf, preprocess_bert

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

@st.cache_resource
def load_model(model_path, model_type):
    """Load model based on type"""
    if model_type == "transformer":
        if TRANSFORMERS_AVAILABLE:
            return pipeline("text-classification", model=model_path, tokenizer=model_path)
        else:
            st.error("Transformers library not available")
            return None
    else:
        return joblib.load(model_path)

def predict_with_model(model, texts, model_type, preprocess_type):
    """Make predictions with appropriate preprocessing"""
    # Preprocess texts
    if preprocess_type == "tfidf":
        processed_texts = [preprocess_tfidf(text) for text in texts]
    else:  # bert
        processed_texts = [preprocess_bert(text) for text in texts]
    
    if model_type == "transformer":
        results = model(processed_texts)
        predictions = [1 if r['label'] == 'LABEL_1' else 0 for r in results]
    else:
        predictions = model.predict(processed_texts)
    
    return predictions