import streamlit as st
import pandas as pd
from model_loader import predict_with_model

def render_text_tester(results):
    """Render text input testing interface"""
    st.header("🧪 Text Testing")
    st.markdown("Test individual text samples with all loaded models")
    
    if not results:
        st.info("No models loaded. Please run evaluation first to test text samples.")
        return
    
    # Text input
    st.subheader("Input Text")
    test_text = st.text_area(
        "Enter text to test:",
        placeholder="Masukkan teks yang ingin diuji untuk deteksi promosi judi online...",
        height=100
    )
    
    # Prediction button
    col1, col2 = st.columns([1, 4])
    with col1:
        predict_button = st.button("🔍 Predict", type="primary")
    
    if predict_button and test_text.strip():
        st.subheader("Prediction Results")
        
        # Get model components from session state if available
        if 'model_components_cache' not in st.session_state:
            st.warning("Model components not cached. Please run evaluation first.")
            return
        
        # Make predictions with each model
        prediction_results = []
        
        for model_name in results.keys():
            if model_name in st.session_state.model_components_cache:
                try:
                    model_components = st.session_state.model_components_cache[model_name]
                    model_config = st.session_state.model_configs_cache[model_name]
                    
                    # Make prediction for single text
                    prediction = predict_single_text(model_components, test_text, model_config)
                    
                    prediction_results.append({
                        'Model': model_name,
                        'Prediction': 'Gambling Promotion' if prediction == 1 else 'Normal Text',
                        'Confidence': 'High' if prediction in [0, 1] else 'Low',
                        'Value': prediction
                    })
                    
                except Exception as e:
                    prediction_results.append({
                        'Model': model_name,
                        'Prediction': 'Error',
                        'Confidence': 'N/A',
                        'Value': f"Error: {str(e)}"
                    })
        
        # Display results
        if prediction_results:
            results_df = pd.DataFrame(prediction_results)
            
            # Color code the results
            def color_prediction(val):
                if val == 'Gambling Promotion':
                    return 'background-color: #ffebee'
                elif val == 'Normal Text':
                    return 'background-color: #e8f5e8'
                else:
                    return 'background-color: #fff3e0'
            
            styled_df = results_df.style.applymap(color_prediction, subset=['Prediction'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Summary
            gambling_count = sum(1 for r in prediction_results if r['Value'] == 1)
            normal_count = sum(1 for r in prediction_results if r['Value'] == 0)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Models Predicting Gambling", gambling_count)
            with col2:
                st.metric("Models Predicting Normal", normal_count)
            with col3:
                consensus = "Gambling" if gambling_count > normal_count else "Normal" if normal_count > gambling_count else "Split"
                st.metric("Consensus", consensus)
            
            # Detailed analysis
            if len(prediction_results) > 1:
                st.subheader("Analysis")
                if gambling_count == len(prediction_results):
                    st.success("🚨 **All models agree**: This text is likely a gambling promotion")
                elif normal_count == len(prediction_results):
                    st.success("✅ **All models agree**: This text appears to be normal")
                elif gambling_count > normal_count:
                    st.warning(f"⚠️ **Majority prediction**: {gambling_count}/{len(prediction_results)} models predict gambling promotion")
                elif normal_count > gambling_count:
                    st.info(f"ℹ️ **Majority prediction**: {normal_count}/{len(prediction_results)} models predict normal text")
                else:
                    st.error("🤔 **Split decision**: Models are evenly divided")
        
    elif predict_button and not test_text.strip():
        st.warning("Please enter some text to test.")

def predict_single_text(model_components, text, model_config):
    """Make prediction for a single text sample"""
    model_type = model_config['architecture']
    
    if model_type == "tfidf_rf":
        from preprocessing import preprocess_tfidf
        processed_text = preprocess_tfidf(text)
        X = model_components['vectorizer'].transform([processed_text])
        prediction = model_components['classifier'].predict(X)[0]
        return int(prediction)
    
    elif model_type in ["indobert_rf", "indobert_svm"]:
        from preprocessing import preprocess_bert
        from model_loader import extract_bert_features_batch
        
        processed_text = preprocess_bert(text)
        X = extract_bert_features_batch([processed_text], 
                                       model_components['tokenizer'], 
                                       model_components['bert_model'])
        prediction = model_components['classifier'].predict(X)[0]
        return int(prediction)
    
    elif model_type == "indobert_bilstm":
        from preprocessing import preprocess_bert
        import torch
        
        processed_text = preprocess_bert(text)
        tokenizer = model_components['tokenizer']
        bilstm_model = model_components['bilstm']
        bilstm_model.eval()
        
        inputs = tokenizer(processed_text, padding='max_length', truncation=True, 
                         max_length=128, return_tensors='pt')
        
        with torch.no_grad():
            output = bilstm_model(inputs['input_ids'], inputs['attention_mask'])
            prediction = (output > 0.5).float().item()
            return int(prediction)
    
    elif model_type == "indobert_finetuned":
        from preprocessing import preprocess_bert
        import torch
        
        processed_text = preprocess_bert(text)
        tokenizer = model_components['tokenizer']
        model = model_components['model']
        model.eval()
        
        inputs = tokenizer(processed_text, return_tensors='pt', padding=True, 
                         truncation=True, max_length=128)
        
        with torch.no_grad():
            outputs = model(**inputs)
            prediction = torch.argmax(outputs.logits, dim=-1).item()
            return int(prediction)
    
    return 0  # Default fallback