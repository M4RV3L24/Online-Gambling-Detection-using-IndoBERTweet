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
        # Load BiLSTM model
        checkpoint = torch.load(model_config['bilstm_path'], map_location='cpu')
        
        # Check if it's a complete model or state dict
        if hasattr(checkpoint, 'eval'):
            # Complete model object
            bilstm_model = checkpoint
        elif isinstance(checkpoint, dict):
            # State dict - try to extract model if available
            if 'model' in checkpoint:
                bilstm_model = checkpoint['model']
            elif 'model_state_dict' in checkpoint:
                st.error("BiLSTM saved as state_dict only. Need complete model or architecture definition.")
                st.info("Please save the complete model using torch.save(model, path) instead of torch.save(model.state_dict(), path)")
                return None
            else:
                # Assume it's the state dict itself
                st.error("BiLSTM model is a state dictionary. Need model architecture to load.")
                st.info("Please provide the complete model file or define the model architecture in code.")
                return None
        else:
            st.error(f"Unknown BiLSTM model format: {type(checkpoint)}")
            return None
            
        return {'bilstm': bilstm_model}
    
    elif model_type == "indobert_finetuned":
        # Load fine-tuned IndoBERTweet directly with PyTorch
        if TRANSFORMERS_AVAILABLE:
            try:
                from transformers import AutoModelForSequenceClassification
                tokenizer = AutoTokenizer.from_pretrained(model_config['model_path'])
                model = AutoModelForSequenceClassification.from_pretrained(model_config['model_path'])
                return {'tokenizer': tokenizer, 'model': model}
            except Exception as e:
                st.error(f"Error loading fine-tuned model: {str(e)}")
                return None
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

def predict_with_model(model_components, texts, model_config, preprocessed_bert_texts=None):
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
        # Use preprocessed texts if available
        processed_texts = preprocessed_bert_texts if preprocessed_bert_texts else [preprocess_bert(text) for text in texts]
        # Extract BERT features
        X = extract_bert_features(processed_texts, model_components['tokenizer'], 
                                model_components['bert_model'])
        # Predict
        predictions = model_components['classifier'].predict(X)
        return predictions
    
    elif model_type == "indobert_bilstm":
        # Use preprocessed texts if available
        processed_texts = preprocessed_bert_texts if preprocessed_bert_texts else [preprocess_bert(text) for text in texts]
        # Direct prediction with complete BiLSTM model
        model_components['bilstm'].eval()
        predictions = []
        for text in processed_texts:
            with torch.no_grad():
                output = model_components['bilstm'](text)
                pred = (torch.sigmoid(output) > 0.5).int().item()
                predictions.append(pred)
        return predictions
    
    elif model_type == "indobert_finetuned":
        # Use preprocessed texts if available
        processed_texts = preprocessed_bert_texts if preprocessed_bert_texts else [preprocess_bert(text) for text in texts]
        # Direct prediction with fine-tuned model
        tokenizer = model_components['tokenizer']
        model = model_components['model']
        model.eval()
        
        predictions = []
        for text in processed_texts:
            inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=128)
            with torch.no_grad():
                outputs = model(**inputs)
                pred = torch.argmax(outputs.logits, dim=-1).item()
                predictions.append(pred)
        return predictions
    
    return []

def get_model_configs():
    """Return predefined model configurations with default paths"""
    return {
        "TF-IDF + Random Forest": {
            "architecture": "tfidf_rf",
            "default_vectorizer_path": "Model/rf_tfidf/tfidf_vectorizer.pkl",
            "default_classifier_path": "Model/rf_tfidf/rf_model_best.pkl"
        },
        "IndoBERTweet + Random Forest": {
            "architecture": "indobert_rf",
            "default_base_path": "Model/base-model-indobertweet",
            "default_classifier_path": "Model/ml_indobertweet/rf_model_best.pkl"
        },
        "IndoBERTweet + SVM": {
            "architecture": "indobert_svm",
            "default_base_path": "Model/base-model-indobertweet",
            "default_classifier_path": "Model/ml_indobertweet/svc_model_best.pkl"
        },
        "IndoBERTweet + BiLSTM": {
            "architecture": "indobert_bilstm",
            "default_bilstm_path": "Model/indobertweet_bilstm_model.pt"
        },
        "Fine-tuned IndoBERTweet": {
            "architecture": "indobert_finetuned",
            "default_model_path": "Model/indobertweet_finetuned_judol"
        }
    }