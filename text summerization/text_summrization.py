import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from string import punctuation
from heapq import nlargest
import PyPDF2

def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in range(reader.numPages):
            page_text = reader.getPage(page).extractText()
            text += page_text
        return text

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

pdf_file = r'C:\Users\Manas\Documents\example.pdf'
raw_text = "This is an example raw text."

# Generate summary from PDF file
pdf_summary, pdf_doc, pdf_original_length, pdf_summary_length = summarizer(read_pdf(pdf_file))

# Generate summary from raw text
text_summary, text_doc, text_original_length, text_summary_length = summarizer(raw_text)

print('PDF Summary:', pdf_summary)
print('PDF Original Length:', pdf_original_length)
print('PDF Summary Length:', pdf_summary_length)

print('Text Summary:', text_summary)
print('Text Original Length:', text_original_length)
print('Text Summary Length:', text_summary_length)
