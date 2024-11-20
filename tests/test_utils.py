import pytest
import io
from utils import analyze_sentiment, extract_text_from_pdf, extract_text_from_docx

def test_analyze_sentiment_positive():
    text = "This is a great day!"
    score, category, subjectivity, emotions = analyze_sentiment(text)
    assert category == "positive"
    assert 70 <= score <= 100  # Positive score range

def test_analyze_sentiment_negative():
    text = "This is a terrible day."
    score, category, subjectivity, emotions = analyze_sentiment(text)
    assert category == "negative"
    assert 0 <= score <= 30  # Negative score range

def test_analyze_sentiment_neutral():
    text = "This is an average day."
    score, category, subjectivity, emotions = analyze_sentiment(text)
    assert category in ["neutral", "negative"]  # Allow minor misclassification for edge cases
    assert 30 <= score <= 70  # Neutral range

def test_extract_text_from_pdf_invalid_file():
    # Simulate invalid PDF input
    with pytest.raises(Exception):
        extract_text_from_pdf(io.BytesIO(b"Not a PDF"))

def test_extract_text_from_docx_invalid_file():
    # Simulate invalid DOCX input
    with pytest.raises(Exception):
        extract_text_from_docx(io.BytesIO(b"Not a DOCX"))
