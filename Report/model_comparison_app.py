import streamlit as st
import pandas as pd
import json
import tempfile
import os
from model_loader import load_model_components, predict_with_model, get_model_configs
from metrics import calculate_metrics
from ui_components import (
    render_sidebar, render_dataset_overview, render_metrics_comparison,
    render_metrics_visualization, render_confusion_matrices, render_best_model,
    render_model_config, render_classification_report
)

st.set_page_config(page_title="Model Performance Comparison", layout="wide")

@st.cache_data
def load_test_data(file_path):
    if file_path.endswith('.json'):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return pd.DataFrame(data)
    else:
        return pd.read_csv(file_path)

def main():
    st.title("🔍 Online Gambling Promotion Detection - Model Comparison")
    st.markdown("**Tujuan**: Membandingkan performa model klasifikasi untuk mendeteksi promosi judi online dalam teks")
    
    # Render sidebar
    test_file, models_config = render_sidebar()
    
    # Check if we have test file and at least one model
    def has_required_files(config):
        arch = config['architecture']
        if arch == 'tfidf_rf':
            return config.get('use_default') or (config.get('vectorizer_file') and config.get('classifier_file'))
        elif arch in ['indobert_rf', 'indobert_svm']:
            return config.get('use_default') or (config.get('base_model_path') and config.get('classifier_file'))
        elif arch == 'indobert_bilstm':
            return config.get('use_default') or config.get('bilstm_file')
        elif arch == 'indobert_finetuned':
            return config.get('use_default') or config.get('model_path')
        return False
    
    has_models = any(has_required_files(config) for config in models_config)
    
    if test_file and has_models:
        # Load test data
        if test_file.name.endswith('.json'):
            data = json.load(test_file)
            df = pd.DataFrame(data)
        else:
            df = pd.read_csv(test_file)
        
        render_dataset_overview(df)
        
        # Create a unique key for caching based on file and model config
        cache_key = f"{test_file.name}_{hash(str(models_config))}"
        
        # Check if results are already cached
        if 'results' not in st.session_state or st.session_state.get('cache_key') != cache_key:
            # Load models and make predictions
            results = {}
            for config in models_config:
                if has_required_files(config):
                    try:
                        # Prepare config with temporary file paths
                        temp_config = config.copy()
                        
                        # Use default paths or uploaded files
                        if config['architecture'] == 'tfidf_rf':
                            if config.get('use_default'):
                                vectorizer_path = 'Model/rf_tfidf/tfidf_vectorizer.pkl'
                                classifier_path = 'Model/rf_tfidf/rf_model_best.pkl'
                                
                                if not os.path.exists(vectorizer_path):
                                    st.error(f"Vectorizer file not found: {vectorizer_path}")
                                    continue
                                if not os.path.exists(classifier_path):
                                    st.error(f"Classifier file not found: {classifier_path}")
                                    continue
                                    
                                temp_config['vectorizer_path'] = vectorizer_path
                                temp_config['classifier_path'] = classifier_path
                            else:
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_vec:
                                    tmp_vec.write(config['vectorizer_file'].read())
                                    temp_config['vectorizer_path'] = tmp_vec.name
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_clf:
                                    tmp_clf.write(config['classifier_file'].read())
                                    temp_config['classifier_path'] = tmp_clf.name
                                
                        elif config['architecture'] in ['indobert_rf', 'indobert_svm']:
                            if config.get('use_default'):
                                classifier_path = config.get('default_classifier_path')
                                
                                if not os.path.exists(classifier_path):
                                    st.error(f"Classifier file not found: {classifier_path}")
                                    continue
                                    
                                temp_config['base_model_path'] = config.get('default_base_path', 'indolem/indobertweet-base-uncased')
                                temp_config['classifier_path'] = classifier_path
                            else:
                                temp_config['base_model_path'] = config['base_model_path']
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_clf:
                                    tmp_clf.write(config['classifier_file'].read())
                                    temp_config['classifier_path'] = tmp_clf.name
                                
                        elif config['architecture'] == 'indobert_bilstm':
                            if config.get('use_default'):
                                bilstm_path = 'Model/indobertweet_bilstm_model.pt'
                                
                                if not os.path.exists(bilstm_path):
                                    st.error(f"BiLSTM model file not found: {bilstm_path}")
                                    continue
                                    
                                temp_config['bilstm_path'] = bilstm_path
                            else:
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.pt') as tmp_bilstm:
                                    tmp_bilstm.write(config['bilstm_file'].read())
                                    temp_config['bilstm_path'] = tmp_bilstm.name
                        
                        # Set default model path for finetuned
                        if config['architecture'] == 'indobert_finetuned' and config.get('use_default'):
                            model_path = config.get('default_model_path')
                            
                            if not os.path.exists(model_path):
                                st.error(f"Fine-tuned model not found: {model_path}")
                                continue
                                
                            temp_config['model_path'] = model_path
                        
                        # Load model components
                        model_components = load_model_components(temp_config, config['name'])
                        
                        if model_components is not None:
                            # Add model name to config to avoid caching conflicts
                            temp_config['name'] = config['name']
                            
                            # Create section for this model's progress
                            st.subheader(f"Processing {config['name']}")
                            
                            # Pass actual labels for preview functionality
                            predictions = predict_with_model(
                                model_components, 
                                df['text'].tolist(), 
                                temp_config,
                                actual_labels=df['label'].tolist()
                            )
                            
                            metrics = calculate_metrics(df['label'], predictions)
                            results[config['name']] = {
                                'predictions': predictions,
                                'metrics': metrics,
                                'architecture': config['architecture']
                            }
                    except Exception as e:
                        st.error(f"Error loading model {config['name']}: {str(e)}")
            
            # Cache results and dataframe
            st.session_state.results = results
            st.session_state.df = df
            st.session_state.cache_key = cache_key
        else:
            # Use cached results
            results = st.session_state.results
            df = st.session_state.df
        
        if results:
            render_metrics_comparison(results)
            render_metrics_visualization(results)
            render_confusion_matrices(results, df)
            render_best_model(results)
            render_model_config(results)
            render_classification_report(results, df)

if __name__ == "__main__":
    main()