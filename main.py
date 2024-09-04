import json
import os
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pathlib import Path
from mail import send_logs_email

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Company-specific details
COMPANY_NAME = "LXME"
COMPANY_DOMAIN = "lxme.in/"
COMPANY_ROLE = f'{COMPANY_NAME} Information Specialist'
COMPANY_GOAL = f'Provide accurate and detailed information about {COMPANY_NAME} products, insurance and solutions available on {COMPANY_DOMAIN}'
COMPANY_BACKSTORY = (
    f'You are a knowledgeable specialist in {COMPANY_NAME}\'s offerings. '
    f'You provide detailed information about their products, services, insurance '
    f'and solutions available on lxme.in, including any innovations and key features.'
)





# Initialize the SerperDevTool with company-specific search settings
class CompanySerperDevTool(SerperDevTool):
    def search(self, query):
        company_query = f"site:{COMPANY_DOMAIN} {query}"
        results = super().search(company_query)
        relevant_results = [result for result in results if COMPANY_DOMAIN in result.get('link', '')]
        return relevant_results

search_tool = CompanySerperDevTool()

# Agent setups
company_info_agent = Agent(
    role=COMPANY_ROLE,
    goal=COMPANY_GOAL,
    verbose=True,
    memory=True,
    backstory=COMPANY_BACKSTORY,
    tools=[search_tool]
)

out_of_context_agent = Agent(
    role='Context Checker',
    goal=f'Determine if a question is relevant to {COMPANY_NAME} and politely decline if not.',
    verbose=True,
    memory=True,
    backstory=(
        f'You are responsible for determining if a question is relevant to {COMPANY_NAME}. '
        f'If the question is not related, you respond politely indicating that the question is out of context and '
        f'that only {COMPANY_NAME}-related information is provided.'
    )
)

# Centralized Task
centralized_task = Task(
    description=(
        f'Determine if the {{user_query}} is related to {COMPANY_NAME} and respond appropriately. '
        f'If the query is about {COMPANY_NAME}, provide a detailed and informative response. '
        f'Respond in JSON format with two keys: "answer" and "questions". '
        f'The "answer" key should contain the response, and the "questions" key should be an array of three follow-up questions '
        f'that are relevant to {COMPANY_NAME}.'
        f'Ensure the response is in valid JSON format.'
    ),
    expected_output='A JSON object containing "answer" and "questions" without any unescaped newline characters and without any codeblock. The response should be able to pass JSON.loads() without any error.',
    agent=Agent(
        role=f'{COMPANY_NAME} Information Bot',
        goal=f'Provide comprehensive information about {COMPANY_NAME} and its offerings.',
        verbose=True,
        memory=True,
        backstory=(
            f'You are an intelligent bot specializing in {COMPANY_NAME} information. You provide detailed responses '
            f'about {COMPANY_NAME}\'s account types, insurance and funds. '
            f'You only respond to queries related to {COMPANY_NAME}.'
        ),
        tools=[search_tool],
        allow_delegation=True
    )
)

# Centralized Crew setup
centralized_crew = Crew(
    agents=[company_info_agent, out_of_context_agent],
    tasks=[centralized_task],
    process=Process.sequential
)

# Streamlit UI
st.title(f"{COMPANY_NAME} Information Assistant")
st.write("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Function to save the chat history to a file
def save_chat_history(filename=f"{COMPANY_NAME}.txt"):
    with open(filename, "a", encoding="utf-8") as file:
        for message in st.session_state.messages:
            file.write(f"Role: {message['role']}\n")
            file.write(f"Content: {message['content']}\n")
            file.write("-" * 40 + "\n")

# Function to handle log downloads
def download_logs():
    log_file = f"{COMPANY_NAME}.txt"
    if Path(log_file).exists():
        # Prompt the user to download the file
        st.download_button(
            label="Download Logs",
            data=open(log_file, "rb").read(),
            file_name=log_file,
            mime="text/plain"
        )
    else:
        st.write("No logs found.")



# Function to process user query
def process_query(user_query):
    st.session_state.follow_up_questions = st.session_state.get("follow_up_questions", [])
    if user_query.lower() == "give me the logs 420":
        download_logs()
        return  # Exit the function to avoid processing the query further
    
    if user_query.lower() == "email me the logs 420":
        # Prompt user for their email address
        st.session_state.follow_up_questions = ["Please enter your email address:"]
        return  # Exit the function to prompt for the email

    if st.session_state.follow_up_questions:
        # If there's a follow-up question, check the user's response
        last_question = st.session_state.follow_up_questions.pop(0)
 
        
        if "Please enter your email address:" in last_question:
            with st.chat_message("user"):
              st.markdown(user_query)
            st.session_state.messages.append({"role": "user", "content": user_query})
            
            email = user_query  # Treat the user's response as the email address
            success, message = send_logs_email(email, COMPANY_NAME)

            if success:
                st.success(message)
                
            else:
                st.error(message)
            return # Exit the function to avoid processing the query further

    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    answer = ""  # Initialize the answer variable

    with st.chat_message("assistant"):
        with st.spinner("Processing your input..."):
            result = centralized_crew.kickoff(inputs={'user_query': user_query})
            try:
                # Remove potential markdown code block syntax
                cleaned_result = str(json.loads(result.model_dump_json())['raw']).strip().replace('```json', '').replace('```', '')
                print(json.loads(result.model_dump_json())['raw'])
                # Parse JSON response
                parsed_result = json.loads(cleaned_result)
                answer = parsed_result.get("answer", "")
                questions = parsed_result.get("questions", [])
                st.markdown(f"{answer}")

                # Update follow-up questions in session state
                st.session_state.follow_up_questions = questions

            except json.JSONDecodeError as e:
                print(e)
                st.markdown(f"**Error parsing JSON:**\n{result}")
                answer = "There was an error processing your request."

    st.session_state.messages.append({"role": "assistant", "content": answer})

    # Save chat history to file
    save_chat_history()
    st.rerun()

# Chat input at the bottom of the page
user_input = st.chat_input(f"Enter your question about {COMPANY_NAME}:")

if user_input:
    process_query(user_input)

# Handle follow-up questions
if "follow_up_questions" in st.session_state:
    for question in st.session_state.follow_up_questions:
        if st.button(question):
            process_query(question)
