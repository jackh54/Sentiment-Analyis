import nltk
nltk.data.path.append('nlkt_data')
nltk.download('vader_lexicon', download_dir='nlkt_data')
import streamlit as st
import time
from datetime import datetime
from utils import (
    analyze_sentiment, get_color_scheme, create_sentiment_chart,
    get_emotion_color, extract_text_from_pdf, extract_text_from_docx,
    create_comparison_chart, get_text_summary, calculate_trend
)

# set up the page with a nice title, icon, and layout
st.set_page_config(
    page_title="Sentiment Analyzer",
    page_icon="🎭",
    layout="wide"
)

# load the custom styles from the css file
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# initialize some storage for user interactions
if 'history' not in st.session_state:
    st.session_state.history = []
if 'comparison_texts' not in st.session_state:
    st.session_state.comparison_texts = []

# show the main title and a brief explanation of the app
st.title("✨ Real-time Sentiment Analyzer")
st.markdown("Enter your text or upload documents to analyze sentiments and emotions in real-time.")

# create the two main sections for analysis options
tab1, tab2 = st.tabs(["Single Analysis", "Comparative Analysis"])

with tab1:
    # layout for single text analysis
    col1, col2 = st.columns(2)
    
    with col1:
        # let the user input text
        text_input = st.text_area(
            "Type or paste your text here",
            height=150,
            key="text_input",
            help="Enter the text you want to analyze"
        )
        
        if text_input:
            # count the number of characters
            char_count = len(text_input)
            st.caption(f"Character count: {char_count}")

    with col2:
        # allow users to upload a document instead of typing
        st.markdown("### Or upload a document")
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["pdf", "docx"],
            help="Upload a PDF or DOCX file for analysis",
            key="single_upload"
        )
        
        if uploaded_file is not None:
            # handle file processing for pdf and docx
            if uploaded_file.type == "application/pdf":
                text_input = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                text_input = extract_text_from_docx(uploaded_file)
                
            if text_input:
                # let the user know the file was processed
                st.success("File processed successfully!")
                char_count = len(text_input)
                st.caption(f"Character count: {char_count}")
            else:
                # show an error if the file couldn't be processed
                st.error("Failed to process the file. Please ensure it contains readable text.")

    # analyze the input text
    if text_input:
        score, category, subjectivity, emotion_scores = analyze_sentiment(text_input)
        
        if score is not None:
            # get the color scheme for the sentiment
            main_color, bg_color, text_color = get_color_scheme(category)
            
            # display results in three sections
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                # display the sentiment score
                st.markdown(
                    f"""
                    <div class="score-indicator" 
                         style="background-color: {main_color}; color: white;">
                        {int(score)}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col2:
                # show the sentiment and subjectivity details
                st.markdown(
                    f"""
                    <div class="sentiment-box" 
                         style="background-color: {bg_color}; color: {text_color};">
                        <h3 style="margin:0;">Sentiment: {category.title()}</h3>
                        <p style="margin:0;">Subjectivity: {int(subjectivity)}%</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            
            with col3:
                # show a breakdown of emotions
                st.markdown("### Emotion Breakdown")
                for emotion, score in emotion_scores.items():
                    color = get_emotion_color(emotion)
                    st.markdown(
                        f"""
                        <div class="emotion-box" 
                             style="background-color: {color}20; 
                                    border-left: 4px solid {color};">
                            <strong>{emotion.title()}:</strong> {int(score)}%
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            
            # keep track of the analysis history
            if len(st.session_state.history) >= 10:
                st.session_state.history.pop(0)
            
            st.session_state.history.append({
                "text": get_text_summary(text_input),
                "score": score,
                "category": category,
                "subjectivity": subjectivity,
                "emotions": emotion_scores,
                "timestamp": datetime.now()
            })

with tab2:
    st.markdown("### Comparative Analysis")
    st.markdown("Add multiple texts to compare their sentiments and emotions.")
    
    # let the user input a text for comparison
    comparison_text = st.text_area(
        "Enter text for comparison",
        height=150,
        key="comparison_text",
        help="Enter the text you want to add to comparison"
    )
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # allow users to upload files for comparison
        uploaded_file = st.file_uploader(
            "Or upload a document",
            type=["pdf", "docx"],
            help="Upload a PDF or DOCX file for comparison",
            key="comparison_upload"
        )
        
        if uploaded_file is not None:
            # handle file processing for comparison
            if uploaded_file.type == "application/pdf":
                comparison_text = extract_text_from_pdf(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                comparison_text = extract_text_from_docx(uploaded_file)
    
    with col2:
        # button to add the current text to the comparison list
        if st.button("Add to Comparison", help="Add the current text to comparison"):
            if comparison_text:
                score, category, subjectivity, emotion_scores = analyze_sentiment(comparison_text)
                if score is not None:
                    st.session_state.comparison_texts.append({
                        "text": get_text_summary(comparison_text),
                        "score": score,
                        "category": category,
                        "subjectivity": subjectivity,
                        "emotions": emotion_scores,
                        "timestamp": datetime.now()
                    })
                    st.success("Text added to comparison!")
            else:
                st.error("Please enter some text or upload a file first.")
        
        # button to clear all texts from comparison
        if st.button("Clear Comparison", help="Clear all texts from comparison"):
            st.session_state.comparison_texts = []
            st.success("Comparison cleared!")
    
    # show the results of the comparison
    if len(st.session_state.comparison_texts) > 1:
        st.markdown("### Comparison Results")
        
        # create a chart comparing the texts
        chart = create_comparison_chart(st.session_state.comparison_texts)
        if chart:
            st.plotly_chart(chart, use_container_width=True)
        
        # display individual text details
        st.markdown("### Text Details")
        for i, item in enumerate(st.session_state.comparison_texts):
            _, bg_color, text_color = get_color_scheme(item["category"])
            emotions_html = "".join([
                f'<span style="color: {get_emotion_color(emotion)};">{emotion.title()}: {int(score)}%</span> | '
                for emotion, score in item["emotions"].items()
            ])
            
            st.markdown(
                f"""
                <div class="history-item" 
                     style="background-color: {bg_color}; color: {text_color};">
                    <strong>Text {i+1}:</strong> {item["text"]}<br>
                    Score: {int(item["score"])} | Category: {item["category"].title()}<br>
                    <small>{emotions_html}</small>
                </div>
                """,
                unsafe_allow_html=True
            )
    elif len(st.session_state.comparison_texts) == 1:
        # remind the user they need at least two texts
        st.info("Add at least one more text to see the comparison.")
    else:
        # tell the user to start adding texts
        st.info("Add texts using the form above to start comparison.")

# show a summary of recent sentiment analyses and trends
if st.session_state.history:
    st.markdown("### Sentiment Trend Analysis")
    
    # calculate and display trends
    trend, slope = calculate_trend(st.session_state.history)
    trend_color = {
        "improving": "#28a745",
        "declining": "#dc3545",
        "stable": "#6c757d"
    }.get(trend, "#6c757d")
    
    st.markdown(
        f"""
        <div style="padding: 10px; border-radius: 5px; background-color: {trend_color}20; 
                    border-left: 4px solid {trend_color}; margin-bottom: 20px;">
            <strong>Current Trend:</strong> {trend.title()}
            {f' (Rate of change: {slope:.2f} points per analysis)' if trend != 'stable' else ''}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # show a chart of the sentiment history
    chart = create_sentiment_chart(st.session_state.history)
    if chart:
        st.plotly_chart(chart, use_container_width=True)
    
    # show details of recent analyses
    st.markdown("### Recent Analyses")
    for item in reversed(st.session_state.history):
        _, bg_color, text_color = get_color_scheme(item["category"])
        emotions_html = "".join([
            f'<span style="color: {get_emotion_color(emotion)};">{emotion.title()}: {int(score)}%</span> | '
            for emotion, score in item.get("emotions", {}).items()
        ])
        
        timestamp_str = item["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        
        st.markdown(
            f"""
            <div class="history-item" 
                 style="background-color: {bg_color}; color: {text_color};">
                <small>{item["text"]}</small><br>
                Score: {int(item["score"])} | Category: {item["category"].title()}<br>
                <small>{emotions_html}</small><br>
                <small>Analyzed at: {timestamp_str}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

# add a little footer with credits
st.markdown("---")
st.markdown(
    "Made with ❤️ using Streamlit | "
    "Sentiment analysis powered by TextBlob and NLTK VADER"
)
