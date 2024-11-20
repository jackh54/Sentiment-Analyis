from textblob import TextBlob
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import docx
from pypdf import PdfReader
import io
import pandas as pd
from datetime import datetime

# make sure required nltk data is available
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('punkt')
    nltk.download('vader_lexicon')

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error processing PDF: {str(e)}")

def extract_text_from_docx(docx_file):
    # deal with extracting text from docx files
    try:
        doc = docx.Document(docx_file)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text.strip()
    except Exception as e:
        st.error(f"Error processing DOCX: {str(e)}")
        return None

def analyze_emotions(text):
    # break down emotions using vader sentiment analysis
    if not text.strip():
        return None, None
    
    sia = SentimentIntensityAnalyzer()
    scores = sia.polarity_scores(text)
    
    # adjust scores to percentages for better readability
    emotion_scores = {
        'joy': max(min((scores['pos'] * 100), 100), 0),
        'sadness': max(min((scores['neg'] * 100), 100), 0),
        'neutral': max(min((scores['neu'] * 100), 100), 0)
    }
    
    # figure out which emotion dominates
    dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
    
    return emotion_scores, dominant_emotion

def analyze_sentiment(text):
    # analyze the text for overall sentiment and subjectivity
    if not text.strip():
        return None, None, None, None
    
    analysis = TextBlob(text)
    # scale polarity to a range of 0-100
    score = (analysis.sentiment.polarity + 1) * 50
    
    # classify sentiment into positive, negative, or neutral
    if analysis.sentiment.polarity > 0.1:
        category = "positive"
    elif analysis.sentiment.polarity < -0.1:
        category = "negative"
    else:
        category = "neutral"
        
    # calculate subjectivity percentage
    subjectivity = analysis.sentiment.subjectivity * 100
    
    # include a breakdown of emotions
    emotion_scores, dominant_emotion = analyze_emotions(text)
    
    return score, category, subjectivity, emotion_scores

def get_color_scheme(category):
    # set colors for sentiment categories
    if category == "positive":
        return "#28a745", "#d4edda", "#155724"
    elif category == "negative":
        return "#dc3545", "#f8d7da", "#721c24"
    return "#6c757d", "#e9ecef", "#383d41"

def get_emotion_color(emotion):
    # assign specific colors for emotions
    colors = {
        'joy': '#FFD700',     # gold
        'sadness': '#4169E1',  # royal blue
        'neutral': '#808080'   # gray
    }
    return colors.get(emotion, '#808080')

def calculate_trend(history):
    # find trends in sentiment over time
    if len(history) < 2:
        return "neutral", 0
    
    recent_scores = [item["score"] for item in history[-5:] if "score" in item]
    if len(recent_scores) < 2:
        return "neutral", 0
        
    slope = (recent_scores[-1] - recent_scores[0]) / len(recent_scores)
    
    if slope > 1:
        trend = "improving"
    elif slope < -1:
        trend = "declining"
    else:
        trend = "stable"
        
    return trend, slope

def create_sentiment_chart(history):
    # build a visual chart to show sentiment history and trends
    if not history:
        return None
    
    # extract timestamps and sentiment scores
    timestamps = [item["timestamp"] for item in history]
    scores = [item["score"] for item in history]
    subjectivity = [item["subjectivity"] for item in history]
    
    # grab emotion scores for each entry
    joy_scores = [item.get("emotions", {}).get("joy", 0) for item in history]
    sadness_scores = [item.get("emotions", {}).get("sadness", 0) for item in history]
    neutral_scores = [item.get("emotions", {}).get("neutral", 0) for item in history]
    
    # compute moving averages for smoother trends
    window = min(3, len(scores))
    if window > 1:
        ma_scores = pd.Series(scores).rolling(window=window).mean()
    else:
        ma_scores = scores
    
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Sentiment Score & Trend', 'Subjectivity', 'Emotion Breakdown'),
        row_heights=[0.4, 0.3, 0.3]
    )
    
    # add sentiment scores and trends to the chart
    fig.add_trace(
        go.Scatter(x=timestamps, y=scores, mode='lines+markers', 
                  line=dict(color='#2E86C1'), name='Sentiment'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=timestamps, y=ma_scores, mode='lines',
                  line=dict(color='#E74C3C', dash='dash'), 
                  name='Trend (Moving Avg)'),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=timestamps, y=subjectivity, mode='lines+markers',
                  line=dict(color='#28a745'), name='Subjectivity'),
        row=2, col=1
    )
    
    # include emotional breakdowns in the visualization
    fig.add_trace(
        go.Scatter(x=timestamps, y=joy_scores, mode='lines+markers',
                  line=dict(color=get_emotion_color('joy')), name='Joy'),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=timestamps, y=sadness_scores, mode='lines+markers',
                  line=dict(color=get_emotion_color('sadness')), name='Sadness'),
        row=3, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=timestamps, y=neutral_scores, mode='lines+markers',
                  line=dict(color=get_emotion_color('neutral')), name='Neutral'),
        row=3, col=1
    )
    
    fig.update_layout(
        height=800,
        showlegend=True,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # make sure the axes are readable
    fig.update_yaxes(range=[0, 100])
    fig.update_xaxes(title_text="Time")
    
    return fig

def create_comparison_chart(texts_data):
    # set up a chart to compare multiple texts
    if not texts_data:
        return None
    
    fig = make_subplots(rows=2, cols=1, 
                       subplot_titles=('Sentiment Analysis Comparison', 
                                     'Emotion Analysis Comparison'),
                       row_heights=[0.5, 0.5])
    
    # grab data for sentiment and subjectivity comparison
    labels = [f"Text {i+1}" for i in range(len(texts_data))]
    sentiment_scores = [data["score"] for data in texts_data]
    subjectivity_scores = [data["subjectivity"] for data in texts_data]
    
    # plot sentiment scores
    fig.add_trace(
        go.Bar(name='Sentiment Score', x=labels, y=sentiment_scores,
               marker_color='#2E86C1'),
        row=1, col=1
    )
    
    # plot subjectivity scores
    fig.add_trace(
        go.Bar(name='Subjectivity', x=labels, y=subjectivity_scores,
               marker_color='#28a745'),
        row=1, col=1
    )
    
    # prepare data for emotion breakdown
    emotions_data = {
        'joy': [data["emotions"]["joy"] for data in texts_data],
        'sadness': [data["emotions"]["sadness"] for data in texts_data],
        'neutral': [data["emotions"]["neutral"] for data in texts_data]
    }
    
    # add emotion data to the chart
    for emotion, scores in emotions_data.items():
        fig.add_trace(
            go.Bar(name=emotion.title(), x=labels, y=scores,
                  marker_color=get_emotion_color(emotion)),
            row=2, col=1
        )
    
    # set up the chart layout
    fig.update_layout(
        height=800,
        showlegend=True,
        barmode='group',
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    # keep emotion scales consistent
    fig.update_yaxes(range=[0, 100])
    
    return fig

def get_text_summary(text):
    # return a short version of the text
    return text[:50] + "..." if len(text) > 50 else text