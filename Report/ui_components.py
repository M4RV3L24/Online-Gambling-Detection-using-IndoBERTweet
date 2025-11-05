import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import confusion_matrix, classification_report

def render_sidebar():
    """Render sidebar for file uploads and model configuration"""
    st.sidebar.header("Upload Files")
    
    # Test dataset upload
    test_file = st.sidebar.file_uploader("Upload Test Dataset", type=['csv', 'json'])
    
    # Model configuration
    st.sidebar.subheader("Model Configuration")
    num_models = st.sidebar.number_input("Number of Models", min_value=1, max_value=10, value=3)
    
    models_config = []
    for i in range(num_models):
        st.sidebar.write(f"**Model {i+1}**")
        name = st.sidebar.text_input(f"Model {i+1} Name", f"Model_{i+1}", key=f"name_{i}")
        model_type = st.sidebar.selectbox(f"Model {i+1} Type", ["sklearn", "transformer"], key=f"type_{i}")
        preprocess_type = st.sidebar.selectbox(f"Model {i+1} Preprocessing", ["tfidf", "bert"], key=f"preprocess_{i}")
        
        if model_type == "transformer":
            model_path = st.sidebar.text_input(f"Model {i+1} Path/HuggingFace ID", key=f"path_{i}")
            model_file = None
        else:
            model_file = st.sidebar.file_uploader(f"Upload Model {i+1}", type=['pkl', 'joblib'], key=f"file_{i}")
            model_path = None
        
        models_config.append({
            'name': name,
            'type': model_type,
            'preprocess': preprocess_type,
            'file': model_file,
            'path': model_path
        })
    
    return test_file, models_config

def render_dataset_overview(df):
    """Render dataset overview metrics"""
    st.subheader("📊 Dataset Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Samples", len(df))
    with col2:
        st.metric("Spam Count", sum(df['label']))
    with col3:
        st.metric("Ham Count", len(df) - sum(df['label']))

def render_metrics_comparison(results):
    """Render performance metrics comparison table"""
    st.subheader("📈 Performance Metrics Comparison")
    metrics_df = pd.DataFrame({name: data['metrics'] for name, data in results.items()}).T
    st.dataframe(metrics_df.round(4), use_container_width=True)

def render_metrics_visualization(results):
    """Render metrics visualization charts"""
    st.subheader("📊 Metrics Visualization")
    fig = make_subplots(rows=2, cols=2, 
                      subplot_titles=['Accuracy', 'Precision', 'Recall', 'F1-Score'])
    
    metrics = ['Accuracy', 'Precision', 'Recall', 'F1-Score']
    positions = [(1,1), (1,2), (2,1), (2,2)]
    
    for i, metric in enumerate(metrics):
        row, col = positions[i]
        values = [results[name]['metrics'][metric] for name in results.keys()]
        fig.add_trace(
            go.Bar(x=list(results.keys()), y=values, name=metric, showlegend=False),
            row=row, col=col
        )
    
    fig.update_layout(height=600, title_text="Model Performance Comparison")
    st.plotly_chart(fig, use_container_width=True)

def render_confusion_matrices(results, df):
    """Render confusion matrices for all models"""
    st.subheader("🎯 Confusion Matrices")
    cols = st.columns(len(results))
    
    for i, (name, data) in enumerate(results.items()):
        with cols[i]:
            cm = confusion_matrix(df['label'], data['predictions'])
            fig = px.imshow(cm, text_auto=True, aspect="auto", 
                          title=f"{name} Confusion Matrix",
                          labels=dict(x="Predicted", y="Actual"))
            st.plotly_chart(fig, use_container_width=True)

def render_best_model(results):
    """Highlight best performing model"""
    st.subheader("🏆 Best Performing Model")
    best_model = max(results.keys(), key=lambda x: results[x]['metrics']['F1-Score'])
    st.success(f"**{best_model}** achieved the highest F1-Score: {results[best_model]['metrics']['F1-Score']:.4f}")

def render_model_config(results):
    """Render model configuration table"""
    st.subheader("🔧 Model Configuration")
    config_data = []
    for name, data in results.items():
        config_data.append({
            'Model': name,
            'Type': data['type'],
            'Preprocessing': data['preprocess']
        })
    config_df = pd.DataFrame(config_data)
    st.dataframe(config_df, use_container_width=True)

def render_classification_report(results, df):
    """Render detailed classification report"""
    st.subheader("📋 Detailed Classification Reports")
    selected_model = st.selectbox("Select Model for Detailed Report", list(results.keys()))
    
    if selected_model:
        report = classification_report(df['label'], results[selected_model]['predictions'], 
                                     target_names=['Ham', 'Spam'], output_dict=True)
        report_df = pd.DataFrame(report).transpose()
        st.dataframe(report_df.round(4), use_container_width=True)