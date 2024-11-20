# Sentiment and Emotion Analyzer
[![Python application](https://github.com/jackh54/Sentiment-Analyis/actions/workflows/python-app.yml/badge.svg)](https://github.com/jackh54/Sentiment-Analyis/actions/workflows/python-app.yml)

This is a Python-based application that analyzes sentiment and emotions from text using **TextBlob**, **NLTK**, and **VADER**. It provides visualizations for sentiment trends and comparative analysis for multiple texts.

## Live Preview

Check out the live preview of the app:

- https://jackh54-sentiment-analyis.streamlit.app/

## Features

- **Text Sentiment Analysis**: Analyze the overall sentiment (positive, neutral, negative) and subjectivity of input text.
- **Emotion Breakdown**: Detailed emotion analysis (joy, sadness, neutral) using VADER.
- **File Support**: Extract text from PDF and DOCX files for analysis.
- **Trend Analysis**: Visualize trends in sentiment over time.
- **Comparative Analysis**: Compare sentiment and emotions across multiple texts.

## Technologies Used

- **Python Libraries**:
  - `TextBlob`
  - `NLTK` (VADER Sentiment Analyzer)
  - `PyPDF2`
  - `docx`
  - `plotly`
  - `pandas`
- **Streamlit**: For creating an interactive web app.

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/jackh54/Sentiment-Analyis.git
   cd sentiment-analyis
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run main.py
   ```
   - Set a custom port with `--server.port ....` at the end.

4. Open the app in your browser (default is [http://localhost:8501](http://localhost:8501)).

## Usage

- **Single Analysis**:
  - Type or paste text in the input box.
  - Upload PDF or DOCX files to analyze their content.
  - View the sentiment score, category, subjectivity, and emotion breakdown.

- **Comparative Analysis**:
  - Add multiple texts or files to compare their sentiments and emotions side-by-side.

- **Trend Visualization**:
  - Analyze historical sentiment data with trendlines and moving averages.

## Visualizations

- **Sentiment Score & Trend**: Displays the sentiment score over time with a moving average.
- **Subjectivity**: Visualizes the subjectivity of analyzed texts.
- **Emotion Breakdown**: Shows how emotions like joy, sadness, and neutral vary across texts.

## License

This project is open-source and available under the MIT License.
