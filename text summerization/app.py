from flask import Flask, render_template, request
from PyPDF2 import PdfReader
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
//
app = Flask(__name__)

def read_pdf(file):
    reader = PdfReader(file)
    text = ''
    for page in reader.pages:
        text += page.extract_text()
    return text
//
def summarizer(rawdocs):
    stopwords = list(STOP_WORDS)
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(rawdocs)

    tokens = [token.text for token in doc]

    word_freq = {}
    for word in doc:
        if word.text.lower() not in stopwords and word.text.lower() not in punctuation:
            word_freq[word.text] = 1
        else:
            if word_freq.get(word.text) == None:
                word_freq[word.text] = 1
            else:
                word_freq[word.text] = word_freq.get(word.text) + 1

    max_freq = max(word_freq.values())

    for word in word_freq.keys():
        word_freq[word] = word_freq[word] / max_freq

    sent_tokens = [sent for sent in doc.sents]

    sent_scores = {}
    for sent in sent_tokens:
        for word in sent:
            if word.text in word_freq.keys():
                if sent not in sent_scores.keys():
                    sent_scores[sent] = word_freq[word.text]
                else:
                    sent_scores[sent] += word_freq[word.text]

    select_len = int(len(sent_tokens) * 0.3)

    summary = nlargest(select_len, sent_scores, key=sent_scores.get)

    final_summary = [word.text for word in summary]
    summary = ' '.join(final_summary)

    return summary, doc, len(rawdocs.split(' ')), len(summary.split(' '))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summary', methods=['POST'])
def summarization():
    summary = ""  # Initialize the variable with a default value
    original_txt = ""  # Initialize the variable with a default value
    len_orig_txt = 0  # Initialize the variable with a default value
    len_summary = 0  # Initialize the variable with a default value
    if 'file' in request.files:
        pdf_file = request.files['file']
        rawdocs = read_pdf(pdf_file)
        summary, original_txt, len_orig_txt, len_summary = summarizer(rawdocs)
        return render_template('summary.html', original_txt=original_txt, len_orig_txt=len_orig_txt, len_summary=len_summary, summary=summary)
    elif 'rawtext' in request.form:
        raw_text = request.form['rawtext']
        summary, original_txt, len_orig_txt, len_summary = summarizer(raw_text)
        return render_template('summary.html', original_txt=original_txt, len_orig_txt=len_orig_txt,  len_summary=len_summary, summary=summary)
    else:
        return 'No file or text uploaded.'

if __name__ == '__main__':
    app.run(debug=True)
