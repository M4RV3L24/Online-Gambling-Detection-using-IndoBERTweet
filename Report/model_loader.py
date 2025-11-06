import joblib
import pickle
import numpy as np
import streamlit as st
from preprocessing import preprocess_tfidf, preprocess_bert
import pandas as pd

try:
    from transformers import pipeline, AutoTokenizer, AutoModel
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False


@st.cache_resource
def load_model_components(model_config, _model_name=None):
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
        return {'tokenizer': tokenizer, 'bert_model': bert_model, 'classifier': classifier, 'model_type': model_type}
    
    elif model_type == "indobert_bilstm":
        # Define BiLSTM architecture
        import torch.nn as nn
        
        class IndoBERTweetBiLSTM(nn.Module):
            def __init__(self, bert_model, max_length=128):
                super(IndoBERTweetBiLSTM, self).__init__()
                self.bert = bert_model
                self.lstm = nn.LSTM(input_size=768, hidden_size=64, num_layers=1, 
                                    batch_first=True, bidirectional=True)
                self.dropout = nn.Dropout(0.3)
                self.fc = nn.Linear(64 * 2 * max_length, 1)
                self.sigmoid = nn.Sigmoid()

            def forward(self, input_ids, attention_mask):
                with torch.no_grad():
                    outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
                    last_hidden_state = outputs.last_hidden_state
                lstm_out, _ = self.lstm(last_hidden_state)
                x = self.dropout(lstm_out)
                x = x.contiguous().view(x.size(0), -1)
                x = self.fc(x)
                return self.sigmoid(x)
        
        # Load base IndoBERTweet model
        tokenizer = AutoTokenizer.from_pretrained(model_config.get('base_model_path', 'indolem/indobertweet-base-uncased'))
        bert_model = AutoModel.from_pretrained(model_config.get('base_model_path', 'indolem/indobertweet-base-uncased'))
        
        # Create BiLSTM model
        bilstm_model = IndoBERTweetBiLSTM(bert_model)
        
        # Load state dict
        checkpoint = torch.load(model_config['bilstm_path'], map_location='cpu')
        
        if hasattr(checkpoint, 'eval'):
            # Complete model object
            return {'bilstm': checkpoint, 'tokenizer': tokenizer}
        elif isinstance(checkpoint, dict):
            if 'model' in checkpoint:
                return {'bilstm': checkpoint['model'], 'tokenizer': tokenizer}
            else:
                # Load state dict into model
                bilstm_model.load_state_dict(checkpoint)
                return {'bilstm': bilstm_model, 'tokenizer': tokenizer}
        else:
            st.error(f"Unknown BiLSTM model format: {type(checkpoint)}")
            return None
    
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

def extract_bert_features(texts, tokenizer, bert_model, model_name, progress_bar=None, status_text=None, max_length=128, batch_size=32):
    """Extract features from IndoBERTweet with mean pooling and progress tracking"""
    features = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        # Tokenize batch
        inputs = tokenizer(batch_texts, max_length=max_length, padding='max_length', 
                          truncation=True, return_tensors='pt')
        
        # Get BERT embeddings for batch
        with torch.no_grad():
            outputs = bert_model(**inputs)
            
            # Mean pooling instead of CLS
            token_embeddings = outputs.last_hidden_state
            attention_mask = inputs['attention_mask']
            
            # Apply attention mask and calculate mean
            input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
            sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
            sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
            mean_embeddings = sum_embeddings / sum_mask
            
            features.extend(mean_embeddings.numpy())
        
        # Update progress
        if progress_bar is not None and status_text is not None:
            progress = min((i + batch_size) / len(texts), 1.0)
            progress_bar.progress(progress * 0.8)  # Reserve 20% for prediction
            status_text.text(f"{model_name}: Extracting features {min(i + batch_size, len(texts))}/{len(texts)}")
    
    return np.array(features)

def predict_with_model(model_components, texts, model_config, preprocessed_bert_texts=None, actual_labels=None):
    """Make predictions based on model architecture with progress tracking"""
    model_type = model_config['architecture']
    model_name = model_config.get('name', model_type)
    
    if model_type == "tfidf_rf":
        # Batch preprocessing with progress bar
        batch_size = 1000
        all_predictions = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        preview_container = st.container()
        
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i+batch_size]
            # Preprocess batch
            processed_batch = [preprocess_tfidf(text) for text in batch_texts]
            # Vectorize batch
            X_batch = model_components['vectorizer'].transform(processed_batch)
            # Predict batch
            batch_predictions = model_components['classifier'].predict(X_batch)
            all_predictions.extend(batch_predictions)
            
            # Update progress
            progress = min((i + batch_size) / len(texts), 1.0)
            progress_bar.progress(progress)
            status_text.text(f"{model_name}: Processed {min(i + batch_size, len(texts))}/{len(texts)} samples")
            
            # Show preview every 1000 samples
            if len(all_predictions) >= 1000 and len(all_predictions) % 1000 == 0 and actual_labels is not None:
                show_prediction_preview(preview_container, all_predictions, actual_labels, 
                                      texts, model_name, len(all_predictions))
        
        return np.array(all_predictions)
    
    elif model_type in ["indobert_rf", "indobert_svm"]:
        # Use preprocessed texts if available
        processed_texts = preprocessed_bert_texts if preprocessed_bert_texts else [preprocess_bert(text) for text in texts]
        
        # Progress tracking for BERT feature extraction
        progress_bar = st.progress(0)
        status_text = st.empty()
        preview_container = st.container()
        
        status_text.text(f"{model_name}: Extracting BERT features...")
        X = extract_bert_features(processed_texts, model_components['tokenizer'], 
                                model_components['bert_model'], model_name, progress_bar, status_text)
        
        status_text.text(f"{model_name}: Making predictions...")
        predictions = model_components['classifier'].predict(X)
        
        # Show final preview
        if actual_labels is not None:
            show_prediction_preview(preview_container, predictions, actual_labels, 
                                  texts, model_name, len(predictions))
        
        progress_bar.progress(1.0)
        status_text.text(f"{model_name}: Completed {len(predictions)} predictions")
        
        return predictions
    
    elif model_type == "indobert_bilstm":
        # Use preprocessed texts if available
        processed_texts = preprocessed_bert_texts if preprocessed_bert_texts else [preprocess_bert(text) for text in texts]
        
        tokenizer = model_components['tokenizer']
        bilstm_model = model_components['bilstm']
        bilstm_model.eval()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        preview_container = st.container()
        
        predictions = []
        for i, text in enumerate(processed_texts):
            # Tokenize input
            inputs = tokenizer(text, padding='max_length', truncation=True, 
                             max_length=128, return_tensors='pt')
            
            with torch.no_grad():
                output = bilstm_model(inputs['input_ids'], inputs['attention_mask'])
                pred = (output > 0.5).float().item()
                predictions.append(int(pred))
            
            # Update progress
            if (i + 1) % 100 == 0 or i == len(processed_texts) - 1:
                progress = (i + 1) / len(processed_texts)
                progress_bar.progress(progress)
                status_text.text(f"{model_name}: Processed {i + 1}/{len(processed_texts)} samples")
                
                # Show preview every 500 samples
                if len(predictions) >= 500 and len(predictions) % 500 == 0 and actual_labels is not None:
                    show_prediction_preview(preview_container, predictions, actual_labels, 
                                          texts, model_name, len(predictions))
        
        return predictions
    
    elif model_type == "indobert_finetuned":
        # Use preprocessed texts if available
        processed_texts = preprocessed_bert_texts if preprocessed_bert_texts else [preprocess_bert(text) for text in texts]
        
        tokenizer = model_components['tokenizer']
        model = model_components['model']
        model.eval()
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        preview_container = st.container()
        
        predictions = []
        for i, text in enumerate(processed_texts):
            inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=128)
            
            with torch.no_grad():
                outputs = model(**inputs)
                pred = torch.argmax(outputs.logits, dim=-1).item()
                predictions.append(pred)
            
            # Update progress
            if (i + 1) % 100 == 0 or i == len(processed_texts) - 1:
                progress = (i + 1) / len(processed_texts)
                progress_bar.progress(progress)
                status_text.text(f"{model_name}: Processed {i + 1}/{len(processed_texts)} samples")
                
                # Show preview every 500 samples
                if len(predictions) >= 500 and len(predictions) % 500 == 0 and actual_labels is not None:
                    show_prediction_preview(preview_container, predictions, actual_labels, 
                                          texts, model_name, len(predictions))
        
        return predictions
    
    return []

def show_prediction_preview(container, predictions, actual_labels, texts, model_name, processed_count):
    """Show preview of predictions vs actual labels"""
    with container:
        st.write(f"**{model_name} - Preview ({processed_count} processed)**")
        
        # Show last 5 predictions
        preview_data = []
        start_idx = max(0, len(predictions) - 5)
        
        for i in range(start_idx, len(predictions)):
            if i < len(actual_labels):
                preview_data.append({
                    'Index': i + 1,
                    'Text': texts[i][:50] + '...' if len(texts[i]) > 50 else texts[i],
                    'Predicted': predictions[i],
                    'Actual': int(actual_labels[i]),
                    'Match': '✓' if predictions[i] == actual_labels[i] else '✗'
                })
        
        if preview_data:
            import pandas as pd
            df = pd.DataFrame(preview_data)
            st.dataframe(df, use_container_width=True)
            
            # Quick accuracy for processed samples
            correct = sum(1 for i in range(len(predictions)) if i < len(actual_labels) and predictions[i] == actual_labels[i])
            accuracy = correct / min(len(predictions), len(actual_labels)) * 100
            st.write(f"Current accuracy: {accuracy:.1f}% ({correct}/{min(len(predictions), len(actual_labels))})")

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