import streamlit as st
import pandas as pd
import json
import tempfile
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
            return config.get('vectorizer_file') and config.get('classifier_file')
        elif arch in ['indobert_rf', 'indobert_svm']:
            return config.get('base_model_path') and config.get('classifier_file')
        elif arch == 'indobert_bilstm':
            return config.get('base_model_path') and config.get('bilstm_file')
        elif arch == 'indobert_finetuned':
            return config.get('model_path')
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
        
        # Load models and make predictions
        results = {}
        for config in models_config:
            if has_required_files(config):
                try:
                    # Prepare config with temporary file paths
                    temp_config = config.copy()
                    
                    # Save uploaded files temporarily
                    if config['architecture'] == 'tfidf_rf':
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_vec:
                            tmp_vec.write(config['vectorizer_file'].read())
                            temp_config['vectorizer_path'] = tmp_vec.name
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_clf:
                            tmp_clf.write(config['classifier_file'].read())
                            temp_config['classifier_path'] = tmp_clf.name
                            
                    elif config['architecture'] in ['indobert_rf', 'indobert_svm']:
                        temp_config['base_model_path'] = config['base_model_path']
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_clf:
                            tmp_clf.write(config['classifier_file'].read())
                            temp_config['classifier_path'] = tmp_clf.name
                            
                    elif config['architecture'] == 'indobert_bilstm':
                        temp_config['base_model_path'] = config['base_model_path']
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pth') as tmp_bilstm:
                            tmp_bilstm.write(config['bilstm_file'].read())
                            temp_config['bilstm_path'] = tmp_bilstm.name
                    
                    # Load model components
                    model_components = load_model_components(temp_config)
                    
                    if model_components is not None:
                        predictions = predict_with_model(model_components, df['text'].tolist(), temp_config)
                        metrics = calculate_metrics(df['label'], predictions)
                        results[config['name']] = {
                            'predictions': predictions,
                            'metrics': metrics,
                            'architecture': config['architecture']
                        }
                except Exception as e:
                    st.error(f"Error loading model {config['name']}: {str(e)}")
        
        if results:
            render_metrics_comparison(results)
            render_metrics_visualization(results)
            render_confusion_matrices(results, df)
            render_best_model(results)
            render_model_config(results)
            render_classification_report(results, df)

if __name__ == "__main__":
    main()