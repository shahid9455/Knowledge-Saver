import streamlit as st
import requests
import json

# Set your API key and base URL
api_key = "503f1a51dca844fab06296904b908f01"
base_url = "https://api.aimlapi.com"

# Define headers for authentication
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

def generate_faq(content, keyword):
    # Define the payload with the provided content and keyword
    data = {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        "messages": [
            {
                "role": "system",
                "content": f"You are an AI assistant that generates FAQ questions and answers based on the following content: '{content}'"
            },
            {
                "role": "user",
                "content": f"Generate an FAQ question and answer for the keyword: '{keyword}' based only on the provided content."
            },
        ]
    }

    # Make a POST request to the API
    response = requests.post(f"{base_url}/v1/chat/completions", headers=headers, json=data)

    # Handle the response
    if response.status_code == 200:
        # Extract and clean the content from the API response
        result = response.json()["choices"][0]["message"]["content"].strip()

        # Clean up the result to only include question and answer
        if result.startswith("Here is an FAQ question and answer based on the keyword"):
            result = result.split("\n\n", 1)[-1].strip()  # Remove introductory text

        # Ensure we only get the question and answer part
        if "Q:" in result and "A:" in result:
            question_start = result.find("Q:")
            answer_start = result.find("A:")
            
            question = result[question_start:].split("\n", 1)[0].strip()
            answer = result[answer_start:].strip()
            
            return f"{question}\n{answer}"
        else:
            return result
    else:
        return f"Failed to get a response: {response.status_code} - {response.text}"

# Streamlit app
st.title("FAQ Generator")

# Input fields
content = st.text_area("Enter the content here...", height=200)
keyword = st.text_input("Enter the keyword here...")

if st.button("Generate FAQ"):
    if content and keyword:
        faq = generate_faq(content, keyword)
        st.markdown(faq)  # Output as markdown
    else:
        st.warning("Please enter both content and keyword.")
