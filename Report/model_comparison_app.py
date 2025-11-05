import streamlit as st
import pandas as pd
import json
import tempfile
from model_loader import load_model, predict_with_model
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
    st.title("🔍 Model Performance Comparison Dashboard")
    
    # Render sidebar
    test_file, models_config = render_sidebar()
    
    # Check if we have test file and at least one model
    has_models = any(config['file'] is not None or config['path'] for config in models_config)
    
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
            if config['file'] is not None or config['path']:
                try:
                    if config['type'] == 'transformer':
                        if not config['path']:
                            st.warning(f"No path specified for transformer model {config['name']}")
                            continue
                        model = load_model(config['path'], 'transformer')
                    else:
                        if config['file'] is None:
                            continue
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.pkl') as tmp_file:
                            tmp_file.write(config['file'].read())
                            tmp_path = tmp_file.name
                        model = load_model(tmp_path, 'sklearn')
                    
                    if model is not None:
                        predictions = predict_with_model(model, df['text'].tolist(), config['type'], config['preprocess'])
                        metrics = calculate_metrics(df['label'], predictions)
                        results[config['name']] = {
                            'predictions': predictions,
                            'metrics': metrics,
                            'type': config['type'],
                            'preprocess': config['preprocess']
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