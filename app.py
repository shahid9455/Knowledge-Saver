from flask import Flask, render_template, request, redirect, url_for, flash
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_watson.natural_language_understanding_v1 import Features, KeywordsOptions
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import difflib
import requests
import os

app = Flask(__name__, template_folder='')

app.secret_key = "secret_key_for_flask"

# IBM Watson NLU Configuration
api_key_watson = 'IHbYzsY18Sl7i3Wr-_9YrYjpARDKZRnkO2ETjR5mfvnP'
nlu_url = 'https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/3f07153d-defe-42a0-8215-b0d2d480d44f'

# Initialize IBM Watson NLU
authenticator = IAMAuthenticator(api_key_watson)
nlu = NaturalLanguageUnderstandingV1(
    version='2021-08-01',
    authenticator=authenticator
)
nlu.set_service_url(nlu_url)

# AIML API Configuration
class AIMLClient:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def chat_completions_create(self, model, messages):
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        data = {"model": model, "messages": messages}
        response = requests.post(f"{self.base_url}/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        return response.json()

aiml_client = AIMLClient(api_key="45228194012549f09d70dd18da5ff8a8", base_url="https://api.aimlapi.com")

# Define the filename where text will be stored
filename = 'text_storage_with_keywords.txt'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/save_text', methods=['POST'])
def save_text():
    text = request.form.get('text')
    if text:
        try:
            response = nlu.analyze(
                text=text,
                features=Features(keywords=KeywordsOptions(limit=5))
            ).get_result()
            
            keywords = [kw['text'] for kw in response['keywords']]
            keyword_string = ', '.join(keywords)
            
            with open(filename, 'a') as file:
                file.write(f"Text: {text}\nKeywords: {keyword_string}\n\n")
            
            flash("Your input and extracted keywords have been saved successfully.", "success")
        except Exception as e:
            flash(f"An error occurred while processing the text: {str(e)}", "danger")
    else:
        flash("No text entered to save.", "warning")
    
    return redirect(url_for('index'))

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    refined_text = ""
    suggestions = []

    if query:
        try:
            # Read the text file and get all keywords
            with open(filename, 'r') as file:
                lines = file.readlines()
                all_keywords = []
                all_texts = []

                for line in lines:
                    if 'Keywords:' in line:
                        stored_keywords = [kw.strip() for kw in line.replace('Keywords:', '').split(',')]
                        all_keywords.extend(stored_keywords)
                    if 'Text:' in line:
                        all_texts.append(line.replace('Text:', '').strip())

                # Provide suggestions based on close matches
                suggestions = difflib.get_close_matches(query, all_keywords, n=5, cutoff=0.6)

            # Search for matching texts
            matching_texts = [text for text in all_texts if any(kw.lower() in text.lower() for kw in suggestions)]

            if matching_texts:
                # Generate refined text using the AIML model
                response = aiml_client.chat_completions_create(
                    model="meta-llama/Meta-Llama-3-8B-Instruct-Lite",
                    messages=[
                        {"role": "system", "content": "You are an AI assistant who knows everything."},
                        {"role": "user", "content": f"Refine the following text into a professional and polished summary without asking for additional data:\n\n{' '.join(matching_texts)}"}
                    ]
                )
                refined_text = response['choices'][0]['message']['content'].strip()
                if not refined_text:
                    refined_text = "No refined text generated."
            else:
                refined_text = f"No matching content found for '{query}'."
        except Exception as e:
            refined_text = f"An error occurred: {str(e)}"
    else:
        flash("Please enter a query to search.", "warning")

    return render_template('index.html', refined_text=refined_text, suggestions=suggestions)

if __name__ == "__main__":
    app.run(debug=True)
