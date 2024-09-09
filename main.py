import streamlit as st
import openai

# Initialize OpenAI API key
openai.api_key = 'your_openai_api_key'

def rephrase_text(input_text):
    # Call OpenAI API for rephrasing
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Rephrase the following text:\n\n{input_text}",
        max_tokens=150,
        temperature=0.7,
    )
    return response.choices[0].text.strip()

# Feedback mechanism - simple dictionary (you can expand this or use a DB)
feedback_dict = {}

def submit_feedback(user_input, rephrased_text, feedback):
    feedback_dict[user_input] = {'rephrased': rephrased_text, 'feedback': feedback}
    st.success("Feedback submitted!")

# Streamlit UI
st.title("Text Rephraser with Feedback")

# Input from the user
user_input = st.text_area("Enter text to be rephrased:", "")
if st.button("Rephrase"):
    if user_input:
        rephrased_text = rephrase_text(user_input)
        st.write("Rephrased Text:")
        st.write(rephrased_text)

        # Feedback input
        feedback = st.text_area("Provide feedback on the rephrased text:", "")
        if st.button("Submit Feedback"):
            submit_feedback(user_input, rephrased_text, feedback)
    else:
        st.warning("Please enter text for rephrasing.")

# Display all feedback (for demo purposes)
if feedback_dict:
    st.subheader("Feedback received:")
    for original_text, data in feedback_dict.items():
        st.write(f"Original: {original_text}")
        st.write(f"Rephrased: {data['rephrased']}")
        st.write(f"Feedback: {data['feedback']}")
