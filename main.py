import json
import os
import openai
from pathlib import Path
import streamlit as st
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool
from dotenv import load_dotenv
from pytube import YouTube, Channel
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter

from mail import send_logs_email

# Load environment variables from .env file
load_dotenv()

# Set up the environment keys
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["SERPER_API_KEY"] = os.getenv("SERPER_API_KEY")

# Company-specific details
COMPANY_NAME = "IIT Jammu"
COMPANY_DOMAIN = "iitjammu.ac.in/"
COMMPANY_YOUTUBE = "Airing IIT Jammu"
COMPANY_ROLE = f'{COMPANY_NAME} Information Specialist'
COMPANY_GOAL = f'Provide accurate and detailed information about {COMPANY_NAME} products, services, and solutions available on axi.com.'
COMPANY_BACKSTORY = (
    f'You are a knowledgeable specialist in {COMPANY_NAME}\'s offerings. '
    f'You provide detailed information about their products, services, '
    f'and solutions available on axi.com, including any innovations and key features.'
)


# Load transcription data from the text file
def load_transcriptions(filepath):
    transcriptions = []
    with open(filepath, 'r') as file:
        transcription_data = file.read().split('\n\n\n')  # Assume each entry is separated by double newlines
        for entry in transcription_data:
            lines = entry.strip().split('\n')
            if len(lines) >= 3:
                video_title = lines[0].split(':')[0]
                video_link = lines[0].split(':')[1]
                transcript = '\n'.join(lines[2:])
                transcriptions.append({
                    'title': video_title,
                    'link': video_link,
                    'transcript': transcript
                })
    return transcriptions

transcriptions = load_transcriptions('data.txt')


# Initialize the SerperDevTool with company-specific search settings
class CompanySerperDevTool(SerperDevTool):
    def search(self, query):
        # Search the company website
        print('pratjam weas jeejjs')
        company_query = f"site:{COMPANY_DOMAIN} {query}"
        results = super().search(company_query)
        print('wsefwd')
        print(results)
        relevant_results = [result for result in results if COMPANY_DOMAIN in result.get('link', '')]
        
        # Search through transcriptions
        transcription_results = []
        for transcription in transcriptions:
            if query.lower() in transcription['transcript'].lower():
                transcription_results.append({
                    'title': transcription['title'],
                    'link': transcription['link'],
                    'transcript': transcription['transcript']
                })
        
        return results

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
    expected_output='A JSON object containing "answer", and "questions" without any unescaped newline characters and without any codeblock. It should also have all the links of youtube and blogs it thought during the proccess of searching in json as "links". Make sure to not add links to "answer". The response should be able to pass JSON.loads() without any error. ',
    agent=Agent(
        role=f'{COMPANY_NAME} Information Bot',
        goal=f'Provide comprehensive information about {COMPANY_NAME} and its offerings.',
        verbose=True,
        memory=True,
        backstory=(
            f'You are an intelligent bot specializing in {COMPANY_NAME} information. You provide detailed responses '
            f'about {COMPANY_NAME}\'s trading platforms, learning platform. '
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



# Define custom CSS
custom_css = """
<style>
/* Change the background color of the entire app */
body {
    background-color: #ffe6f2;
}

/* Change the color of the main title */
h1 {
    color: #dc3545;
}

/* Style the chat messages */
.chat-message.user {
    background-color: #ffcccb;
    color: #dc3545;
    border: 2px solid #dc3545;
}

.chat-message.assistant {
    background-color: #ffffcc;
    color: #dc3545;
    border: 2px solid #dc3545;
}

/* Style the input box at the bottom */
.stTextInput > div {
    background-color: #ffcccb;
    border-radius: 5px;
    color: #dc3545;
}

/* Style the buttons */
button {
    background-color: #dc3545;
    color: #fff;
   
    border: none;
    border-radius: 5px;
}

.st-emotion-cache-1ghhuty{
background-color: #dc3545;
}

.st-emotion-cache-bho8sy{
background-color: #ffc107;
}
/* Style the spinner */
.stSpinner > div {
    border-top-color: #dc3545;
}

/* Style the download button */
.stDownloadButton {
    background-color: #dc3545;
    color: #fff;
    border-radius: 5px;
}

.st-emotion-cache-1dp5vir{
background-image: linear-gradient(90deg, rgb(255, 75, 75), rgb(255, 253, 128));
}

.black-text {
    
    color: black;
    
}
</style>
"""

# Inject the custom CSS
st.markdown(custom_css, unsafe_allow_html=True)

# Streamlit UI
st.markdown("""
          
    <img class="logo-footer" style=margin-right:3%; src="https://d2tpnh780x5es.cloudfront.net/rebrand-prod/onla2r0j/logo-red2.svg" alt="AxiCorp">        
    <h4 style="color:#ffc107;">
           Customer Support
    </h4>
  
""", unsafe_allow_html=True)
st.write("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def process_chunk(chunk, query):
    # Send a query to the GPT model using a chunk of data
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are telling user about a youtube video."},
            {"role": "user", "content": f"Using the following transcript of a youtube video, answer the query directly:\n\n{chunk}\n\nQuery: {query}"}
        ],
        max_tokens=1500,  # Adjust token limit based on your needs
        temperature=0.7
    )
    # Extract the response from GPT
    return response.choices[0].message.content

def process_large_document(document, query):
    chunk_size = 1000  # Define the chunk size (e.g., 1000 characters)
    chunks = [document[i:i + chunk_size] for i in range(0, len(document), chunk_size)]

    
    for chunk in chunks:
        response = process_chunk(chunk, query)
        aggregated_response = response

    return aggregated_response
#Function to check links

def check_links(links, user_query):
    web_links = []
    youtube_links = []
    youtube_response = ""
    for link in links:
       if COMPANY_DOMAIN in link:
           web_links.append(link)
       if "youtube.com" in link and "watch" in link:
           x = YouTube(link)
           curl = x.channel_url
           c = Channel(curl)
           name = c.channel_name
         
           if name == COMMPANY_YOUTUBE:
               youtube_links.append(link)
   
       
               

               
               
    
    return web_links, youtube_links
           

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
    
    final_answer = ""  # Initialize the answer variable

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
                links = parsed_result.get("links", "")
                web, youtube = check_links(links, user_query)
                questions = parsed_result.get("questions", [])
                link_text = " "
                
                if len(youtube)>0:
                    
                    link_text += '\nHere some youtube references\n' + '\n'
                    for link in youtube:
                    
                         link_text += '\n' + link + '\n' +','
                    
                
                if len(web)>0:
                    link_text += '\nHere some web references\n' + '\n'
                    for link in web:
                        
                        link_text += '\n' + link + ','
                    


                
                final_answer = answer + '\n\nFor your reference:\n' + link_text
                

                # Update follow-up questions in session state
                st.session_state.follow_up_questions = questions

            except json.JSONDecodeError as e:
                print(e)
                st.markdown(f"**Error parsing JSON:**\n{result}")
                answer = "There was an error processing your request."

    st.session_state.messages.append({"role": "assistant", "content": final_answer})
    
    

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
