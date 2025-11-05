import joblib
import pickle
import numpy as np
import streamlit as st
from preprocessing import preprocess_tfidf, preprocess_bert

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from tensorflow.keras.models import load_model as keras_load_model
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

@st.cache_resource
def load_model_components(model_config):
    """Load model components based on architecture"""
    model_type = model_config['architecture']
    
    if model_type == "tfidf_rf":
        # Load TF-IDF vectorizer and Random Forest separately
        vectorizer = joblib.load(model_config['vectorizer_path'])
        classifier = joblib.load(model_config['classifier_path'])
        return {'vectorizer': vectorizer, 'classifier': classifier}
    
    elif model_type in ["indobert_rf", "indobert_svm"]:
        # Load base IndoBERTweet model and classifier
        tokenizer = AutoTokenizer.from_pretrained(model_config['base_model_path'])
        bert_model = AutoModel.from_pretrained(model_config['base_model_path'])
        classifier = joblib.load(model_config['classifier_path'])
        return {'tokenizer': tokenizer, 'bert_model': bert_model, 'classifier': classifier}
    
    elif model_type == "indobert_bilstm":
        # Load PyTorch BiLSTM model from Model folder
        tokenizer = AutoTokenizer.from_pretrained(model_config['base_model_path'])
        bert_model = AutoModel.from_pretrained(model_config['base_model_path'])
        bilstm_model = torch.load(model_config['bilstm_path'], map_location='cpu')
        return {'tokenizer': tokenizer, 'bert_model': bert_model, 'bilstm': bilstm_model}
    
    elif model_type == "indobert_finetuned":
        # Load fine-tuned IndoBERTweet
        if TRANSFORMERS_AVAILABLE:
            return pipeline("text-classification", model=model_config['model_path'], tokenizer=model_config['model_path'])
        else:
            st.error("Transformers library not available")
            return None
    
    return None

def extract_bert_features(texts, tokenizer, bert_model, max_length=128, batch_size=32):
    """Extract features from IndoBERTweet with batching"""
    features = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        # Tokenize batch
        inputs = tokenizer(batch_texts, max_length=max_length, padding='max_length', 
                          truncation=True, return_tensors='pt')
        
        # Get BERT embeddings for batch
        with torch.no_grad():
            outputs = bert_model(**inputs)
            # Use [CLS] token embeddings
            cls_embeddings = outputs.last_hidden_state[:, 0, :].numpy()
            features.extend(cls_embeddings)
    
    return np.array(features)

def predict_with_model(model_components, texts, model_config):
    """Make predictions based on model architecture"""
    model_type = model_config['architecture']
    
    if model_type == "tfidf_rf":
        # Batch preprocessing with progress bar
        batch_size = 1000
        all_predictions = []
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            # Preprocess batch
            processed_batch = [preprocess_tfidf(text) for text in batch_texts]
            # Vectorize batch
            X_batch = model_components['vectorizer'].transform(processed_batch)
            # Predict batch
            batch_predictions = model_components['classifier'].predict(X_batch)
            all_predictions.extend(batch_predictions)
        
        return np.array(all_predictions)
    
    elif model_type in ["indobert_rf", "indobert_svm"]:
        # Preprocess for BERT
        processed_texts = [preprocess_bert(text) for text in texts]
        # Extract BERT features
        X = extract_bert_features(processed_texts, model_components['tokenizer'], 
                                model_components['bert_model'])
        # Predict
        predictions = model_components['classifier'].predict(X)
        return predictions
    
    elif model_type == "indobert_bilstm":
        # Preprocess for BERT
        processed_texts = [preprocess_bert(text) for text in texts]
        # Extract BERT features
        bert_features = extract_bert_features(processed_texts, model_components['tokenizer'], 
                                            model_components['bert_model'])
        # Convert to tensor and predict with PyTorch BiLSTM
        bert_tensor = torch.tensor(bert_features, dtype=torch.float32)
        model_components['bilstm'].eval()
        with torch.no_grad():
            outputs = model_components['bilstm'](bert_tensor)
            predictions = (torch.sigmoid(outputs) > 0.5).int().numpy().flatten()
        return predictions
    
    elif model_type == "indobert_finetuned":
        # Preprocess for BERT
        processed_texts = [preprocess_bert(text) for text in texts]
        # Direct prediction with fine-tuned model
        results = model_components(processed_texts)
        predictions = [1 if r['label'] == 'LABEL_1' else 0 for r in results]
        return predictions
    
    return []

def get_model_configs():
    """Return predefined model configurations"""
    return {
        "TF-IDF + Random Forest": {
            "architecture": "tfidf_rf",
            "vectorizer_path": None,
            "classifier_path": None
        },
        "IndoBERTweet + Random Forest": {
            "architecture": "indobert_rf",
            "base_model_path": None,  # Path to base IndoBERTweet model folder
            "classifier_path": None   # Path to RF classifier pkl
        },
        "IndoBERTweet + SVM": {
            "architecture": "indobert_svm",
            "base_model_path": None,  # Path to base IndoBERTweet model folder
            "classifier_path": None   # Path to SVM classifier pkl
        },
        "IndoBERTweet + BiLSTM": {
            "architecture": "indobert_bilstm",
            "base_model_path": None,  # Path to base IndoBERTweet model folder
            "bilstm_path": None       # Path to PyTorch BiLSTM model
        },
        "Fine-tuned IndoBERTweet": {
            "architecture": "indobert_finetuned",
            "model_path": None        # HuggingFace model path
        }
    }