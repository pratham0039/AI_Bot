import streamlit as st
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables from .env file
load_dotenv()
# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

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


def rephrase_sprinklr(sprinklr_input, generated_prompt):
    # Call OpenAI API to rephrase the Sprinklr input using the generated prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that rephrases text."},
            {"role": "user", "content": f'''

             Chatbot Response: {sprinklr_input} 
             User's emotions: {generated_prompt}            
Rephrase the chatbot's response to address the user's emotions in a way that fosters trust, validation, and hope, while reducing feelings of anger or fear. Separate content from delivery, focusing on what needs to be communicated and how it should be conveyed. Ensure the message is clear, concise, and actionable to minimize cognitive overload for the user.

Reflect the user's emotions and concerns to build rapport and demonstrate understanding, mirroring their frame of mind. Always maintain a solution-oriented approach by providing clear next steps and timelines, reducing uncertainty and anxiety.

Use 'You'-focused sentences to center on the user's needs and concerns (e.g., 'Let's focus on getting this resolved for you'). Choose words that convey action, urgency, and reassurance, while avoiding terms that might trigger negative emotions or increase anxiety.

Validate the user's urgency and importance of a timely resolution (e.g., 'I understand that you need this resolved quickly'). Avoid over-apologizing; instead, emphasize taking action and providing solutions. Start sentences with 'Yes' to create a more agreeable tone, even when disagreeing.

End with a focus on the solution, clearly outlining the next steps and emphasizing what actions are being taken to resolve the issue. Use presuppositions to state facts confidently, reducing uncertainty (e.g., 'Your money is safe' instead of 'Please be assured your money is safe'). Minimize the user's effort by avoiding requests for additional steps or follow-ups, and emphasize proactive communication to keep them updated.

Maintain a conversational and friendly tone throughout, ensuring that the rephrased message never becomes helpless, apologetic, or defensive. Avoid justifying or explaining any inconvenience, pain, or anger caused to the user, and concentrate on what can be done now to resolve the issue.

Your response should be concise, and if possible use bullet points for steps or important information.

Only give the rephrased reponse nothing else.

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

if st.button("Submit"):
    if user_input and sprinklr_input:
        with st.spinner("Processing..."):
            # Step 1: Generate prompt based on user input

            user_emotions = understand_user(user_input)
            

            # Step 2: Rephrase Sprinklr input using the generated prompt
            rephrased_output = rephrase_sprinklr(sprinklr_input, user_emotions)
            st.write("Rephrased Sprinklr Output:")
            st.write(rephrased_output)
    else:
        st.error("Please provide both User and Sprinklr inputs.")
