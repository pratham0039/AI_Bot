import streamlit as st
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import time
import pandas as pd
from io import BytesIO

def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    embedding = response.data[0].embedding
    print(embedding)
    return np.array(embedding)

def calculate_similarity(embedding1, embedding2):
    return cosine_similarity([embedding1], [embedding2])[0][0]

# Load environment variables from .env file
load_dotenv()
# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def load_prompts_from_file(uploaded_file):
    # Load prompts from the uploaded text file
    prompts = uploaded_file.read().decode("utf-8").splitlines()
    return prompts

def understand_user(user_input):
    # Call OpenAI API to understand user's emotion and generate a prompt
    response =client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that understands emotions. "},
            {"role": "user", "content": f"The user says: {user_input}. What is their emotion"}
        ]
    )
    prompt = response.choices[0].message.content
    
    return prompt


def rephrase_sprinklr(sprinklr_input, generated_prompt,prompt):
    # Call OpenAI API to rephrase the Sprinklr input using the generated prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that rephrases text."},
            {"role": "user", "content": f'''

             Chatbot Response: {sprinklr_input} 
             User's emotions: {generated_prompt} 
{prompt}           


'''}
        ]
    )
    rephrased_output = response.choices[0].message.content
    return rephrased_output

# Streamlit app
st.title("Emotion-based Sprinklr Rephraser")



# User input
user_input = st.text_input("Enter User Input:")
sprinklr_input = st.text_area("Enter Sprinklr Input:")
riddhi_input = st.text_area("Enter Riddhi Input:")

uploaded_file = st.file_uploader("Upload a text file with prompts", type=["txt"])

inputs = []
sprinklr_inputs = []
prompts_given = []
prompt_lengths = []
rephrased_outputs = []
times_taken = []
similarity_scores = []

if uploaded_file is not None:
    prompts = load_prompts_from_file(uploaded_file)
    
    st.write("Uploaded Prompts:")
    # Display prompts as a list
    st.markdown("### List of Prompts:")
    for i, prompt in enumerate(prompts, 1):
        st.markdown(f"{i}. {prompt}")

if st.button("Submit"):
    if user_input and sprinklr_input and riddhi_input:
        with st.spinner("Processing..."):
            for i, prompt in enumerate(prompts, 1):
                if len(prompt.split())>2:
                    st.write(i)
                # Step 1: Generate prompt based on user input
                    st.write("prompt")
                    st.write(prompt)
                    prompt_length = len(prompt.split())  # Count the number of words in the prompt
                    st.write(f"Prompt Length: {prompt_length} words")
                    start_time = time.time()

                    user_emotions = understand_user(user_input)
                    

                    # Step 2: Rephrase Sprinklr input using the generated prompt
                    rephrased_output = rephrase_sprinklr(sprinklr_input, user_emotions,prompt)
                    st.write("Rephrased Sprinklr Output:")
                    st.write(rephrased_output)
                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    embedding1 = get_embedding(rephrased_output)
                    embedding2 = get_embedding(riddhi_input)

                    # Calculate cosine similarity
                    similarity_score = calculate_similarity(embedding1, embedding2)

                    st.write("Similarity score")
                    st.write(similarity_score)
                    st.write(f"Time Taken: {elapsed_time:.2f} seconds")
                    inputs.append(user_input)
                    sprinklr_inputs.append(sprinklr_input)
                    prompts_given.append(prompt)
                    prompt_lengths.append(prompt_length)
                    rephrased_outputs.append(rephrased_output)
                    times_taken.append(elapsed_time)
                    similarity_scores.append(similarity_score)

            data = {
                "Input": inputs,
                "Sprinklr Input": sprinklr_inputs,
                "Prompt": prompts_given,
                "Prompt Length (words)": prompt_lengths,
                "Rephrased Output": rephrased_outputs,
                "Time Taken (seconds)": times_taken,
                "Similarity Score": similarity_scores
            }
            df = pd.DataFrame(data)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  # Use 'xlsxwriter' engine
                df.to_excel(writer, index=False, sheet_name='Results')

            # Reset the buffer's position to the beginning
            output.seek(0)

            # Save the file to a download button
            st.download_button(
                label="Download Excel File",
                data=output,
                file_name="results.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("Please provide both User and Sprinklr inputs.")
