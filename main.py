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

def understand_tactics(user_input, sprinklr_input):
    # Call OpenAI API to understand user's emotion and generate a prompt
    response =client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that understands emotions. "},
            {"role": "user", "content": f'''

I need you to generate a list of tactics that should be used when rephrasing this where
the user query is : {user_input} 
the original response is : {sprinklr_input}
These tactics should focus on improving communication, managing user expectations, and maintaining a positive tone while avoiding blame or excessive apologies. Please provide the list in Python list format.
You should not accept your mistake anytime, you have to acknowledge user only when this is someone else's mistale.
Each tactic should focus on a specific communication strategy. You should choose the tactics from the following:tactics = [
    "Use 'You' Focus Sentences",
    "Validate User's Urgency",
    "Choose Words Carefully",
    "End with Solution Orientation",
    "Minimize User Effort",
    "Avoid Over-Apologizing",
    "Use Presuppositions",
    "Limit Apologies",
    "Reframe the Issue",
    "Redirect Blame"
]
Your output should be just a single python list with all the tactics




'''}
        ]
    )
    prompt = response.choices[0].message.content
    
    return prompt


prompts = {
    "Use 'You' Focus Sentences": "Rephrase the original text by centering the response around the user's needs and concerns. Start sentences with 'You' or phrases that emphasize the user’s perspective.",
    
    "Validate User's Urgency": "Rephrase the original text to acknowledge the user's urgency and demonstrate understanding of the importance of resolving the issue quickly. Express empathy and urgency in your response.",
    
    "Choose Words Carefully": "Rephrase the original text by selecting words that convey a sense of action, urgency, and reassurance. Avoid words that might trigger negative emotions or increase anxiety. Use more positive and proactive language.",
    
    "End with Solution Orientation": "Rephrase the original text to ensure that the response ends with a clear focus on the next steps and the actions being taken to resolve the issue. Emphasize what will be done to address the user's concern.",
    
    "Minimize User Effort": "Rephrase the original text to avoid asking the user to take additional steps. Emphasize that you will handle everything and proactively keep them updated without requiring them to follow up.",
    
    "Avoid Over-Apologizing": "Rephrase the original text to show empathy without excessive apologies. Focus on taking action and providing solutions rather than over-apologizing, which can seem insincere or increase annoyance.",
    
    "Use Presuppositions": "Rephrase the original text by stating facts confidently without seeking confirmation from the user. Increase assurance by presenting the situation as something that is already being handled.",
    
    "Limit Apologies": "Rephrase the original text to limit apologies and maintain professionalism. Focus on resolving the issue without accepting fault unless it’s necessary. Keep the tone positive and proactive.",
    
    "Reframe the Issue": "Rephrase the original text to present the situation in a way that shifts focus from any potential fault of the service provider to finding a resolution. Highlight the steps being taken to fix the problem rather than dwelling on the issue itself.",
    
    "Redirect Blame": "Rephrase the original text to subtly shift responsibility away from the service provider without directly blaming others. Focus on external factors like system processes or banking protocols to explain the situation."
}


def understand_scenerio(user_input,sprinklr_input):
    response =client.chat.completions.create(
    model="gpt-4o-mini",
    
    messages=[
        {"role": "system", "content": "You are an assistant that understands emotions. "},
        {"role": "user", "content": f'''

I need you to tell me in which scenerio the user query exists.
the user query is : {user_input} 

Choose a scenerio from this list scenarios = [
    "Greeting and Introduction",
    "Frustration or Anger",
    "Happiness or Satisfaction",
    "General Inquiry",
    "Technical Issues",
    "Transaction Issues",
    "Account Management",
    "Card Services",
    "Loan and Financial Services",
    "Security Concerns",
    "Fee and Charges Inquiry",
    "Feedback or Complaints",
    "Service Availability",
    "Appointment Scheduling"
]

Your response should only contain the scenerio no extra words.




    '''}
        ]
    )
    prompt = response.choices[0].message.content

    return prompt



def understand_tactics_dynamically(user_input, sprinklr_input):
    response =client.chat.completions.create(
    model="gpt-4o-mini",
    
    messages=[
        {"role": "system", "content": "You are an assistant that understands emotions. "},
        {"role": "user", "content": f'''

I need you to generate a list of tactics that should be used when rephrasing this where
the user query is : {user_input} 
the original response is : {sprinklr_input}
These tactics should focus on improving communication, managing user expectations, and maintaining a positive tone while avoiding blame or excessive apologies. Please provide the list in Python list format.
You should not accept your mistake anytime, you have to acknowledge user only when this is someone else's mistale.
Each tactic should focus on a specific communication strategy. such as validating the user's urgency, choosing words carefully, or minimizing user effort.Here's an example of how the list should be structured:

Please provide the final list formatted as a Python list, with each tactic enclosed in double quotes and separated by commas.




    '''}
        ]
    )
    prompt = response.choices[0].message.content

    return prompt



def generate_prompt(tactics_list):
    combined_prompt = []
    
    for tactic in tactics_list:
        if tactic in prompts:
            combined_prompt.append(prompts[tactic])
        else:
            combined_prompt.append(f"No prompt available for the tactic: {tactic}")
    
    # Join all prompts into a single string
    return "\n\n".join(combined_prompt)


def rephrase_sprinklr_dynamically(sprinklr_input, user_input, tactics_list):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,
        messages=[
            {"role": "system", "content": "You are a chatbot response generator using the following tactics."},
            {"role": "user", "content": f'''

             Chatbot Response: {sprinklr_input} 
             User's emotions: {user_input}            
Rephrase the chatbot's response to address the user's emotions in a way that fosters trust, validation, and hope, while reducing feelings of anger or fear. Separate content from delivery, focusing on what needs to be communicated and how it should be conveyed. Ensure the message is clear, concise, and actionable to minimize cognitive overload for the user.

Use these tactics list. {tactics_list}
You should never say sentences like you don't need to, it looks like you are making an order, always use don't need to worry like sentences which gives user hope that we also worry about him.

your output should contain just the rephrase version.



'''}
        ]
    )
    rephrased_output = response.choices[0].message.content
    return rephrased_output




def repharse_sprinklr_scenerio(scenerio, sprinklr_input, tactics_prompt):
    if scenerio in ["Greeting and Introduction", "Happiness or Satisfaction", "General Inquiry","Account Management", "Card Services","Loan and Financial Services","Security Concerns","Service Availability"]:
        prompt = f'''

       
        You are from customer care team, you need to rephrase this text to increase customer satisfaction.
        Your response should be concise
        Maintain a conversational and friendly tone
        You have to rephrase this chatbpot response: {sprinklr_input}
        
    

        '''
    else:
        prompt = f'''

                Chatbot Response: {sprinklr_input} 
                                    
                Rephrase the chatbot's response to address the user's emotions in a way that fosters trust, validation, and hope, while reducing feelings of anger or fear. Separate content from delivery, focusing on what needs to be communicated and how it should be conveyed. Ensure the message is clear, concise, and actionable to minimize cognitive overload for the user.
                You should never say sentences like you don't need to, it looks like you are making an order, always use don't need to worry like sentences which gives user hope that we also worry about him.
                Maintain a conversational and friendly tone throughout, ensuring that the rephrased message never becomes helpless, apologetic, or defensive. Avoid justifying or explaining any inconvenience, pain, or anger caused to the user, and concentrate on what can be done now to resolve the issue.

                Your response should be concise, and if possible use bullet points for steps or important information.
                Reflect the user's emotions and concerns to build rapport and demonstrate understanding, mirroring their frame of mind. Always maintain a solution-oriented approach by providing clear next steps and timelines, reducing uncertainty and anxiety.
                {tactics_prompt}



                '''
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that rephrases text."},
            {"role": "user", "content": f'''{prompt}



        '''}
                ]
        )
    rephrased_output = response.choices[0].message.content
    return rephrased_output


def rephrase_sprinklr(sprinklr_input, generated_prompt, tactics_prompt):
    # Call OpenAI API to rephrase the Sprinklr input using the generated prompt
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that rephrases text."},
            {"role": "user", "content": f'''

             Chatbot Response: {sprinklr_input} 
             User's emotions: {generated_prompt}            
Rephrase the chatbot's response to address the user's emotions in a way that fosters trust, validation, and hope, while reducing feelings of anger or fear. Separate content from delivery, focusing on what needs to be communicated and how it should be conveyed. Ensure the message is clear, concise, and actionable to minimize cognitive overload for the user.
You should never say sentences like you don't need to, it looks like you are making an order, always use don't need to worry like sentences which gives user hope that we also worry about him.
Maintain a conversational and friendly tone throughout, ensuring that the rephrased message never becomes helpless, apologetic, or defensive. Avoid justifying or explaining any inconvenience, pain, or anger caused to the user, and concentrate on what can be done now to resolve the issue.

Your response should be concise, and if possible use bullet points for steps or important information.
Reflect the user's emotions and concerns to build rapport and demonstrate understanding, mirroring their frame of mind. Always maintain a solution-oriented approach by providing clear next steps and timelines, reducing uncertainty and anxiety.
{tactics_prompt}



'''}
        ]
    )
    rephrased_output = response.choices[0].message.content
    return rephrased_output

# Streamlit app
st.title("Tactics based Sprinklr Rephraser")

# User input
user_input = st.text_input("Enter User Input:")
sprinklr_input = st.text_area("Enter Sprinklr Input:")
option = st.selectbox(
    'Choose an option:',
    ['Rephrase using static prompts', 'Rephrase using dynamic response', 'Rephrase with scenerios']
)

if st.button("Submit"):
    if user_input and sprinklr_input:
        if option =='Rephrase using static prompts': 
            with st.spinner("Processing..."):
                # Step 1: Generate prompt based on user input

                user_emotions = understand_tactics(user_input, sprinklr_input)
                st.write(user_emotions)
                tactic_prompt = generate_prompt(user_emotions)
                

                # Step 2: Rephrase Sprinklr input using the generated prompt
                rephrased_output = rephrase_sprinklr(sprinklr_input, user_input, tactic_prompt)
                st.write("Rephrased Sprinklr Output:")
                st.write(rephrased_output)
        elif option =='Rephrase using static prompts':
            with st.spinner("Processing..."):
                tactics_list = understand_tactics_dynamically(user_input, sprinklr_input)
                st.write(tactics_list)
                rephrased_output = rephrase_sprinklr_dynamically(sprinklr_input, user_input, tactics_list)
                st.write("Rephrased Sprinklr Output:")
                st.write(rephrased_output)
        
        else:
            with st.spinner("Processing..."):
                scenerio = understand_scenerio(user_input, sprinklr_input)
                st.write(f'Scenerio: {scenerio}')
                if scenerio in ["Greeting and Introduction", "Happiness or Satisfaction", "General Inquiry","Account Management", "Card Services","Loan and Financial Services","Security Concerns","Service Availability"]:
                    rephrased_output = repharse_sprinklr_scenerio(scenerio,sprinklr_input,[])
                else:
                    tactics_list = understand_tactics_dynamically(user_input, sprinklr_input)
                    st.write(tactics_list)
                    rephrased_output = rephrase_sprinklr_dynamically(sprinklr_input, user_input, tactics_list)

                

  
                
               
                
                st.write("Rephrased Sprinklr Output:")
                st.write(rephrased_output)


                

    else:
        st.error("Please provide both User and Sprinklr inputs.")
