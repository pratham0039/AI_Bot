import streamlit as st
import openai
from dotenv import load_dotenv
import os
from phi.assistant import Assistant
from phi.tools.duckduckgo import DuckDuckGo
from phi.llm.openai import OpenAIChat
from openai import OpenAI

# Load environment variables
load_dotenv()

# Replace with your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


OPENAI_ACCESS_TOKEN =  os.getenv("OPENAI_API_KEY")  # Replace with your actual OpenAI API key

# Create an instance of the Assistant
assistant = Assistant(
    llm=OpenAIChat(
        model="gpt-4o-mini",
        max_tokens=1024,
        temperature=0.9,
        api_key=OPENAI_ACCESS_TOKEN
    ),
    tools=[DuckDuckGo()],
    show_tool_calls=False
)


# Streamlit app starts here
st.set_page_config(page_title="LXME Chatbot", layout="centered")

# Title of the app
st.title("LXME Chatbot")

# Store chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# OpenAI assistant prompt generation function
def get_best_response(user_message, response):
    prompt = f'''
You are a customer service specialist at a company named LXME.
LXME is India's first investment and financial platform specifically designed for women. The platform aims to empower women to achieve financial freedom and confidence in managing their finances. It offers various resources including:

1. **Investment Opportunities**: The LXME app provides options for mutual fund investments, allowing women to invest systematically in line with their financial goals.
2. **Educational Resources**: The site features blogs, guides, and live sessions to enhance financial literacy among women.
3. **Financial Tools**: LXME includes user-friendly financial calculators to assist in personal financial planning.
4. **Community Support**: The platform fosters a community where women can learn, discuss, and share experiences related to finance.

This is more information: {response}
Answer the user query: {user_message}

If the data doesn't have an answer to the user query, tell them you can't find anything related to the query.
Do not remove any reference or link in the information.
If LXME don't have any service or platform user aksed, or the question is not relevant to LXME just let the user know.
'''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    response = response.choices[0].message.content.strip()
    
    return response





def process_query(user_query):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    final_answer = ""  # Initialize the answer variable

    with st.chat_message("assistant"):
        with st.spinner("Processing your input..."):
            try:
                # You may need to simulate searching from LXME's website or use DuckDuckGo for actual queries
                # Example response simulating the search:
                
                # Get the response from OpenAI
                final_query = f"{user_input} site:lxme.in"
                response = assistant.run(final_query, stream=False)
        
                final_answer = get_best_response(user_query, response)

            except Exception as e:
                final_answer = f"There was an error processing your request: {e}"

    st.markdown(final_answer)
    st.session_state.messages.append({"role": "assistant", "content": final_answer})

# Chat input at the bottom of the page
user_input = st.chat_input("Enter your question about LXME:")

if user_input:
    process_query(user_input)
