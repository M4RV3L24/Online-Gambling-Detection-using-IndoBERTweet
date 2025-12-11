import streamlit as st
import pandas as pd
import re
from youtube_comment_downloader import YoutubeCommentDownloader
from text_tester import predict_single_text



def extract_video_id(url):
    """Extract video ID from YouTube URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def download_comments(video_id, limit=100):
    """Download comments from YouTube video"""
    try:
        downloader = YoutubeCommentDownloader()
        comments = []
        
        for comment in downloader.get_comments_from_url(f'https://www.youtube.com/watch?v={video_id}', sort_by=0):
            if len(comments) >= limit:
                break
            comments.append({
                'text': comment['text'],
                'author': comment['author'],
                'votes': comment.get('votes', 0),
                'time': comment.get('time', ''),
                'replies': comment.get('replies', 0)
            })
        
        return comments
    except Exception as e:
        st.error(f"Error downloading comments: {str(e)}")
        return []

def render_youtube_analyzer(results):
    """Render YouTube comment analysis interface"""
    st.header("📺 YouTube Comment Analysis")
    st.markdown("Analyze YouTube video comments for gambling promotion detection")
    
    if not results:
        st.info("No models loaded. Please run evaluation first to analyze YouTube comments.")
        return
    
    # Check if model components are cached
    if 'model_components_cache' not in st.session_state:
        st.warning("Model components not cached. Please run evaluation first.")
        return
    
    # YouTube URL input
    st.subheader("Video Input")
    youtube_url = st.text_input(
        "Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste the full YouTube video URL"
    )
    
    # Comment limit
    col1, col2 = st.columns([2, 1])
    with col1:
        comment_limit = st.slider("Number of comments to analyze:", 10, 500, 100)
    
    with col2:
        analyze_button = st.button("🔍 Analyze Comments", type="primary")
    
    if analyze_button and youtube_url.strip():
        # Extract video ID
        video_id = extract_video_id(youtube_url)
        
        if not video_id:
            st.error("Invalid YouTube URL. Please check the URL format.")
            return
        
        st.info(f"Downloading comments from video: {video_id}")
        
        # Download comments
        with st.spinner("Downloading comments..."):
            comments = download_comments(video_id, comment_limit)
        
        if not comments:
            st.error("No comments found or failed to download comments.")
            return
        
        st.success(f"Downloaded {len(comments)} comments")
        
        # Analyze comments with each model
        st.subheader("Analysis Results")
        
        analysis_results = []
        gambling_comments = []
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, comment in enumerate(comments):
            comment_text = comment['text']
            comment_predictions = {}
            
            # Predict with each model
            for model_name in results.keys():
                if model_name in st.session_state.model_components_cache:
                    try:
                        model_components = st.session_state.model_components_cache[model_name]
                        model_config = st.session_state.model_configs_cache[model_name]
                        
                        prediction = predict_single_text(model_components, comment_text, model_config)
                        comment_predictions[model_name] = prediction
                        
                    except Exception as e:
                        comment_predictions[model_name] = -1  # Error
            
            # Calculate consensus
            valid_predictions = [p for p in comment_predictions.values() if p in [0, 1]]
            if valid_predictions:
                gambling_votes = sum(valid_predictions)
                consensus = 1 if gambling_votes > len(valid_predictions) / 2 else 0
            else:
                consensus = 0
            
            analysis_results.append({
                'comment_id': i + 1,
                'text': comment_text,
                'author': comment['author'],
                'votes': comment['votes'],
                'consensus': consensus,
                **comment_predictions
            })
            
            if consensus == 1:
                gambling_comments.append({
                    'text': comment_text,
                    'author': comment['author'],
                    'votes': comment['votes'],
                    'predictions': comment_predictions
                })
            
            # Update progress
            progress = (i + 1) / len(comments)
            progress_bar.progress(progress)
            status_text.text(f"Analyzed {i + 1}/{len(comments)} comments")
        
        # Create results dataframe
        results_df = pd.DataFrame(analysis_results)
        
        # Summary statistics
        st.subheader("📊 Summary")
        
        total_comments = len(comments)
        gambling_count = len(gambling_comments)
        normal_count = total_comments - gambling_count
        gambling_percentage = (gambling_count / total_comments) * 100
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Comments", total_comments)
        with col2:
            st.metric("Gambling Promotion", gambling_count)
        with col3:
            st.metric("Normal Comments", normal_count)
        with col4:
            st.metric("Gambling %", f"{gambling_percentage:.1f}%")
        
        # Risk assessment
        if gambling_percentage > 20:
            st.error(f"🚨 **High Risk**: {gambling_percentage:.1f}% of comments contain gambling promotions")
        elif gambling_percentage > 10:
            st.warning(f"⚠️ **Medium Risk**: {gambling_percentage:.1f}% of comments contain gambling promotions")
        elif gambling_percentage > 0:
            st.info(f"ℹ️ **Low Risk**: {gambling_percentage:.1f}% of comments contain gambling promotions")
        else:
            st.success("✅ **No Risk**: No gambling promotions detected in comments")
        
        # Model agreement analysis
        st.subheader("🤖 Model Agreement")
        model_stats = {}
        for model_name in results.keys():
            if model_name in results_df.columns:
                model_gambling = sum(results_df[model_name] == 1)
                model_stats[model_name] = {
                    'gambling_detected': model_gambling,
                    'percentage': (model_gambling / total_comments) * 100
                }
        
        model_stats_df = pd.DataFrame(model_stats).T
        st.dataframe(model_stats_df, use_container_width=True)
        
        # Gambling comments details
        if gambling_comments:
            st.subheader("🎰 Detected Gambling Promotions")
            
            for i, comment in enumerate(gambling_comments[:10]):  # Show top 10
                with st.expander(f"Comment {i+1} by {comment['author']} (👍 {comment['votes']})"):
                    st.write(f"**Text:** {comment['text']}")
                    
                    # Show model predictions
                    pred_cols = st.columns(len(comment['predictions']))
                    for j, (model_name, pred) in enumerate(comment['predictions'].items()):
                        with pred_cols[j]:
                            if pred == 1:
                                st.success(f"{model_name}: Gambling")
                            elif pred == 0:
                                st.info(f"{model_name}: Normal")
                            else:
                                st.error(f"{model_name}: Error")
            
            if len(gambling_comments) > 10:
                st.info(f"Showing top 10 of {len(gambling_comments)} gambling promotion comments")
        
        # Download results
        st.subheader("💾 Export Results")
        
        col1, col2 = st.columns(2)
        with col1:
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                "Download Full Analysis (CSV)",
                csv_data,
                f"youtube_analysis_{video_id}.csv",
                "text/csv"
            )
        
        with col2:
            if gambling_comments:
                gambling_df = pd.DataFrame(gambling_comments)
                gambling_csv = gambling_df.to_csv(index=False)
                st.download_button(
                    "Download Gambling Comments (CSV)",
                    gambling_csv,
                    f"gambling_comments_{video_id}.csv",
                    "text/csv"
                )
    
    elif analyze_button and not youtube_url.strip():
        st.warning("Please enter a YouTube URL to analyze.")