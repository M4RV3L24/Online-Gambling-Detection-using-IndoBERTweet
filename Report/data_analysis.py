import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

def render_data_analysis(results, df):
    """Render comprehensive data analysis section"""
    st.header("📊 Exploratory Data Analysis")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "📝 Text Analysis", "🔍 Predictions Analysis", "📋 Full Data View"])
    
    with tab1:
        render_data_overview(df)
    
    with tab2:
        render_text_analysis(df)
    
    with tab3:
        render_predictions_analysis(results, df)
    
    with tab4:
        render_full_data_view(results, df)

def render_data_overview(df):
    """Render basic data overview and statistics"""
    st.subheader("Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Samples", len(df))
    with col2:
        gambling_count = sum(df['label'])
        st.metric("Gambling Promotion", gambling_count)
    with col3:
        normal_count = len(df) - gambling_count
        st.metric("Normal Text", normal_count)
    with col4:
        balance_ratio = min(gambling_count, normal_count) / max(gambling_count, normal_count)
        st.metric("Balance Ratio", f"{balance_ratio:.2f}")
    
    # Label distribution chart
    st.subheader("Label Distribution")
    label_counts = df['label'].value_counts()
    fig = px.pie(values=label_counts.values, names=['Gambling', 'Normal'], 
                 title="Distribution of Labels")
    st.plotly_chart(fig, use_container_width=True)

def render_text_analysis(df):
    """Render text length and content analysis"""
    st.subheader("Text Length Analysis")
    
    # Calculate text lengths
    df_analysis = df.copy()
    df_analysis['text_length'] = df_analysis['text'].str.len()
    df_analysis['word_count'] = df_analysis['text'].str.split().str.len()
    
    # Text length distribution
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.histogram(df_analysis, x='text_length', color='label', 
                          title="Text Length Distribution", nbins=50)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.histogram(df_analysis, x='word_count', color='label', 
                          title="Word Count Distribution", nbins=50)
        st.plotly_chart(fig, use_container_width=True)
    
    # Statistics by label
    st.subheader("Text Statistics by Label")
    stats_data = []
    for label in [True, False]:
        subset = df_analysis[df_analysis['label'] == label]
        stats_data.append({
            'Label': 'Gambling' if label else 'Normal',
            'Avg Length': subset['text_length'].mean(),
            'Avg Words': subset['word_count'].mean(),
            'Max Length': subset['text_length'].max(),
            'Min Length': subset['text_length'].min()
        })
    
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True)
    
    # Word frequency analysis
    st.subheader("Most Common Words")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Gambling Promotion Texts**")
        gambling_texts = ' '.join(df[df['label'] == True]['text'].tolist())
        gambling_words = extract_common_words(gambling_texts)
        gambling_df = pd.DataFrame(gambling_words.most_common(10), columns=['Word', 'Count'])
        st.dataframe(gambling_df, use_container_width=True)
    
    with col2:
        st.write("**Normal Texts**")
        normal_texts = ' '.join(df[df['label'] == False]['text'].tolist())
        normal_words = extract_common_words(normal_texts)
        normal_df = pd.DataFrame(normal_words.most_common(10), columns=['Word', 'Count'])
        st.dataframe(normal_df, use_container_width=True)
    
    # Word clouds
    st.subheader("Word Clouds")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Gambling Promotion Word Cloud**")
        if gambling_texts.strip():
            gambling_clean = clean_text_for_wordcloud(gambling_texts)
            if gambling_clean:
                wordcloud_gambling = WordCloud(width=400, height=300, background_color='white').generate(gambling_clean)
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(wordcloud_gambling, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info("No words available for word cloud")
        else:
            st.info("No gambling texts available")
    
    with col2:
        st.write("**Normal Text Word Cloud**")
        if normal_texts.strip():
            normal_clean = clean_text_for_wordcloud(normal_texts)
            if normal_clean:
                wordcloud_normal = WordCloud(width=400, height=300, background_color='white').generate(normal_clean)
                fig, ax = plt.subplots(figsize=(8, 6))
                ax.imshow(wordcloud_normal, interpolation='bilinear')
                ax.axis('off')
                st.pyplot(fig)
            else:
                st.info("No words available for word cloud")
        else:
            st.info("No normal texts available")

def render_predictions_analysis(results, df):
    """Render analysis comparing predictions across models"""
    st.subheader("Model Predictions Comparison")
    
    if not results:
        st.info("No model results available for analysis.")
        return
    
    # Create prediction comparison dataframe
    comparison_data = []
    for idx, row in df.iterrows():
        data_point = {
            'Index': idx,
            'Text': row['text'][:100] + '...' if len(row['text']) > 100 else row['text'],
            'Actual': int(row['label'])
        }
        
        # Add predictions from each model
        for model_name, model_data in results.items():
            if idx < len(model_data['predictions']):
                data_point[f'{model_name}_Pred'] = int(model_data['predictions'][idx])
        
        comparison_data.append(data_point)
    
    comparison_df = pd.DataFrame(comparison_data)
    
    # Model agreement analysis
    st.subheader("Model Agreement Analysis")
    
    model_names = list(results.keys())
    pred_columns = [f'{name}_Pred' for name in model_names]
    
    # Calculate agreement statistics
    agreement_stats = []
    for i in range(len(comparison_df)):
        predictions = [comparison_df.iloc[i][col] for col in pred_columns]
        actual = comparison_df.iloc[i]['Actual']
        
        # Count agreements
        unanimous = len(set(predictions)) == 1
        majority_pred = max(set(predictions), key=predictions.count)
        correct_models = sum(1 for pred in predictions if pred == actual)
        
        agreement_stats.append({
            'Index': i,
            'Unanimous': unanimous,
            'Majority_Prediction': majority_pred,
            'Actual': actual,
            'Correct_Models': correct_models,
            'Total_Models': len(model_names)
        })
    
    agreement_df = pd.DataFrame(agreement_stats)
    
    col1, col2 = st.columns(2)
    
    with col1:
        unanimous_count = agreement_df['Unanimous'].sum()
        st.metric("Unanimous Predictions", f"{unanimous_count}/{len(agreement_df)} ({unanimous_count/len(agreement_df)*100:.1f}%)")
        
        # Agreement distribution
        fig = px.histogram(agreement_df, x='Correct_Models', 
                          title="Distribution of Correct Models per Sample")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Majority vs actual accuracy
        majority_correct = (agreement_df['Majority_Prediction'] == agreement_df['Actual']).sum()
        st.metric("Majority Vote Accuracy", f"{majority_correct/len(agreement_df)*100:.1f}%")
        
        # Model performance heatmap
        model_correct = []
        for model_name in model_names:
            pred_col = f'{model_name}_Pred'
            correct = (comparison_df[pred_col] == comparison_df['Actual']).sum()
            model_correct.append(correct / len(comparison_df) * 100)
        
        fig = go.Figure(data=go.Bar(x=model_names, y=model_correct))
        fig.update_layout(title="Individual Model Accuracy", yaxis_title="Accuracy (%)")
        st.plotly_chart(fig, use_container_width=True)

def render_full_data_view(results, df):
    """Render full dataset with all predictions"""
    st.subheader("Complete Dataset with Predictions")
    
    if not results:
        st.info("No model results available.")
        return
    
    # Create comprehensive dataframe
    display_df = df.copy()
    display_df['Index'] = range(len(display_df))
    display_df['Actual_Label'] = display_df['label'].astype(int)
    
    # Add predictions from each model
    for model_name, model_data in results.items():
        predictions = model_data['predictions']
        # Ensure predictions list matches dataframe length
        if len(predictions) == len(display_df):
            display_df[f'{model_name}_Prediction'] = [int(p) for p in predictions]
        else:
            st.warning(f"Prediction length mismatch for {model_name}")
    
    # Reorder columns
    cols = ['Index', 'text', 'Actual_Label'] + [col for col in display_df.columns if col.endswith('_Prediction')]
    display_df = display_df[cols]
    
    # Add filters
    st.subheader("Filters")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        label_filter = st.selectbox("Filter by Actual Label:", ["All", "Gambling (1)", "Normal (0)"])
    
    with col2:
        if results:
            model_filter = st.selectbox("Filter by Model Prediction:", ["All"] + list(results.keys()))
        else:
            model_filter = "All"
    
    with col3:
        agreement_filter = st.selectbox("Filter by Agreement:", ["All", "Unanimous", "Disagreement"])
    
    # Apply filters
    filtered_df = display_df.copy()
    
    if label_filter != "All":
        target_label = 1 if "Gambling" in label_filter else 0
        filtered_df = filtered_df[filtered_df['Actual_Label'] == target_label]
    
    if model_filter != "All" and f'{model_filter}_Prediction' in filtered_df.columns:
        prediction_value = st.selectbox(f"Show {model_filter} predictions:", ["All", "Gambling (1)", "Normal (0)"])
        if prediction_value != "All":
            target_pred = 1 if "Gambling" in prediction_value else 0
            filtered_df = filtered_df[filtered_df[f'{model_filter}_Prediction'] == target_pred]
    
    if agreement_filter != "All" and len(results) > 1:
        pred_cols = [col for col in filtered_df.columns if col.endswith('_Prediction')]
        if agreement_filter == "Unanimous":
            # Keep rows where all predictions are the same
            filtered_df = filtered_df[filtered_df[pred_cols].nunique(axis=1) == 1]
        else:  # Disagreement
            # Keep rows where predictions differ
            filtered_df = filtered_df[filtered_df[pred_cols].nunique(axis=1) > 1]
    
    # Display results
    st.write(f"Showing {len(filtered_df)} of {len(display_df)} samples")
    
    # Pagination
    page_size = 50
    total_pages = (len(filtered_df) - 1) // page_size + 1
    
    if total_pages > 1:
        page = st.selectbox("Page:", range(1, total_pages + 1))
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, len(filtered_df))
        page_df = filtered_df.iloc[start_idx:end_idx]
    else:
        page_df = filtered_df
    
    # Display dataframe with styling
    st.dataframe(page_df, use_container_width=True, height=600)
    
    # Download option
    if st.button("Download Filtered Data as CSV"):
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"model_predictions_filtered.csv",
            mime="text/csv"
        )

def extract_common_words(text, min_length=3):
    """Extract common words from text"""
    # Simple word extraction (you can enhance this with proper NLP)
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    # Filter out short words and common stop words
    stop_words = {'dan', 'yang', 'di', 'ke', 'dari', 'untuk', 'pada', 'dengan', 'ini', 'itu', 'adalah', 'akan', 'atau', 'juga', 'tidak', 'ada', 'bisa', 'sudah', 'hanya', 'masih', 'saja', 'lebih', 'dapat', 'seperti', 'karena', 'jika', 'saat', 'setelah', 'oleh', 'antara', 'hingga', 'selama', 'melalui', 'terhadap', 'menurut', 'agar', 'supaya', 'bahwa', 'dimana', 'ketika', 'sambil', 'sedangkan', 'walaupun', 'meskipun', 'kecuali', 'selain'}
    filtered_words = [word for word in words if len(word) >= min_length and word not in stop_words]
    return Counter(filtered_words)

def clean_text_for_wordcloud(text):
    """Clean text for word cloud generation"""
    # Remove URLs, mentions, hashtags, and special characters
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+|#\w+', '', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Extract words and filter
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    stop_words = {'dan', 'yang', 'di', 'ke', 'dari', 'untuk', 'pada', 'dengan', 'ini', 'itu', 'adalah', 'akan', 'atau', 'juga', 'tidak', 'ada', 'bisa', 'sudah', 'hanya', 'masih', 'saja', 'lebih', 'dapat', 'seperti', 'karena', 'jika', 'saat', 'setelah', 'oleh', 'antara', 'hingga', 'selama', 'melalui', 'terhadap', 'menurut', 'agar', 'supaya', 'bahwa', 'dimana', 'ketika', 'sambil', 'sedangkan', 'walaupun', 'meskipun', 'kecuali', 'selain', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an'}
    
    filtered_words = [word for word in words if len(word) >= 3 and word not in stop_words]
    return ' '.join(filtered_words)