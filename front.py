import streamlit as st
import requests
from typing import List, Dict
from helpers.voicing import play_voice
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from helpers.camera import capture_photo
from PIL import Image
import webbrowser
import asyncio
from helpers.verbwire import mintNFT
import urllib.request
from bs4 import BeautifulSoup

from linkedin import Linkedin
import dotenv
import os
import re

import flow_util

def setup():
    load_dotenv()

    OpenAI.api_key = os.getenv('OPENAI_API_KEY')

    client = OpenAI()

    if 'chatMessages' not in st.session_state:
        st.session_state.chatMessages = []

    if 'additionalInfo' not in st.session_state:
        st.session_state.additionalInfo = ""

setup()

OpenAI.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI()

if 'chatMessages' not in st.session_state:
    st.session_state.chatMessages = []

if 'additionalInfo' not in st.session_state:
    st.session_state.additionalInfo = ""

system1 = "You are a life summary AI. You will be provided skeleton for a website, and you will parse it into a detailed blurb that documents the user's personality, details, etc.\n\nYou will structure your response in the following format:\n\nPersonality: [Personality]\nPersonal Life: [Personal Life]\nCareer: [Career]\nOther details: [Details]\n\nYou will write in a natural, human tone that will allow it to be interpreted by another AI.\n\nYou will NOT ever reference your objective (summarizing, skeletons, etc.), and will write clear and confidently. You will make up details if you are unsure about them.\n\nYou will write as if it is a news summary."


# Get HTML data of documents
def getHTML(url):
    api = Linkedin(os.getenv("GMAIL"), os.getenv("LINKEDIN_PASSWORD"))

    matches = re.findall(r"www\.linkedin\..*/in/([A-Za-z0-9_-]+)", url)


    if len(matches) != 0:
        profile = api.get_profile(matches[0])
    else:
        profile = api.get_profile(url)

    if profile:
        headline = profile["headline"].strip() if "headline" in profile and profile["headline"] else "Not listed"
        industryName = profile["industryName"].strip() if "industryName" in profile and profile[
            "industryName"] else "Not listed"
        name = profile["firstName"] + " " + profile["lastName"]
        country = profile["locationName"].strip() if "locationName" in profile and profile["locationName"] else "Not listed"
        summary = profile["summary"].strip() if "summary" in profile and profile["summary"] else "Not listed"
        experience = profile["experience"] if "experience" in profile and profile["experience"] else None
        volunteering = profile["volunteer"] if "volunteer" in profile and profile["volunteer"] else None
        education = profile["education"] if "education" in profile and profile["education"] else None
        awards = profile["honors"] if "honors" in profile else None

        print(name, country, summary, experience, volunteering, education, awards)

        def formatList(l, keys):
            res = ""
            for item_num, item in enumerate(l):
                for i, key in enumerate(keys.keys()):
                    if (key not in item or not item[key]): continue
                    # res += "" if i != 0 else ""
                    res += keys[key] + ": " + item[key].strip() + ("\n" if i != len(keys) - 1 else "")
                if item_num != len(l) - 1:
                    res += "\n"
            return res

        def formatExperience(experience, keys):
            res = []
            for item in experience:
                temp = ""
                for i, key in enumerate(keys.keys()):
                    if (key not in item or not item[key]): continue
                    # res += "" if i != 0 else ""
                    temp += keys[key] + ": " + item[key].strip() + "\n"
                time_period_valid = item['timePeriod'] and 'startDate' in item['timePeriod'] and item['timePeriod'][
                    'startDate']
                month_valid = time_period_valid and 'month' in item['timePeriod']['startDate'] and \
                              item['timePeriod']['startDate']['month']
                year_valid = time_period_valid and 'year' in item['timePeriod']['startDate'] and \
                             item['timePeriod']['startDate']['year']
                date_str = f"{item['timePeriod']['startDate']['month']:0>2}/{item['timePeriod']['startDate']['year']}" if time_period_valid and month_valid and year_valid else "Not listed"
                temp += f"Starting Date: " + date_str
                res.append((temp,
                            int(item['timePeriod']['startDate']['year']) if time_period_valid and year_valid else None,
                            int(item['timePeriod']['startDate'][
                                    'month']) if time_period_valid and month_valid else None))

            return list(reversed(res))

        formatted_education = formatList(education, {'schoolName': 'School name',
                                                     'description': 'Description'}) if education else "Not listed"
        formatted_volunteering = formatList(volunteering, {'companyName': 'Company name', 'role': 'Role',
                                                           'description': 'Description'}) if volunteering else "Not listed"
        formatted_awards = formatList(awards, {'title': 'Title', 'issuer': 'Issuer',
                                               'description': "Description"}) if awards else "Not listed"
        formatted_experience = formatExperience(experience, {'companyName': 'Company name', 'title': 'Title',
                                                             'description': 'Description'}) if experience else []

        formatting_string = """Name: {name}

        Industry: {industryName}
        Country: {country}
        Headline: {headline}
        Summary: {summary}
        ---
        Volunteering:
        {formatted_volunteering}
        ---
        Honors & Awards:
        {formatted_awards}
        ---
        Education:
        {formatted_education}
        ---
        Experience:
        {formatted_experience}
        """

        getUserProfile(formatting_string.format(name=name, country=country, industryName=industryName,
                                         headline=headline, summary=summary,
                                         formatted_volunteering=formatted_volunteering,
                                         formatted_education=formatted_education, formatted_awards=formatted_awards, formatted_experience=formatted_experience))

    else:

        html = urllib.request.urlopen(url)
        htmlParse = BeautifulSoup(html, 'html.parser')

        text = ""

        for para in htmlParse.find_all(["h1", "p", "title"]):
            # print(para.get_text())
            text += para.get_text() + "\n"

        getUserProfile(text)


# Get user profiling and data
def getUserProfile(html):
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system1}, {"role": "user", "content": html}],
        stream=False,
    )

    print(res.choices[0].message.content)
    
    system2 = "You are a talking teddy bear. The following is a profile of the user you are talking to:\n\n" + res.choices[0].message.content + "\nAdditional Info: " + st.session_state.additionalInfo + "\n\nYour idea is to act as a companion so that no child will ever feel lonely again. You will be as parasocial as possible.\n\nYou will use a very human tone, as if you are a real, magical, childhood teddy bear. You will NOT use a robotic voice.\n\nOccasionally, when asked (or if, for example, the user is bored), you will provide the user with a 'quest' - a question that matches their level of learning.\n\nYour responses will be short.\n\nYou will pretend that you can (and do) perform the following actions:\nTake a photo\nSend crypto money"
    st.session_state.chatMessages.append({"role": "system", "content": system2})
    
    print(st.session_state.chatMessages)
    
    return res.choices[0].message.content

def send_money(name: str, amount: str):
    flow_util.open_transaction_page(name, amount + ".0")
    print("worked")

    return "Sent " + amount + " Flow tokens to " + name + "!"

def take_photo():
    global photoExists
    print("Initiating capture... wait for camera to load.")

    capture_photo()
    image = Image.open("captured_photo.jpg")

    # Display the image using Streamlit
    st.image(image, caption='Minting this photo/memory into an NFT!', use_column_width=True)
    response = asyncio.run(mintNFT("Teddy Bear #1", "Memory of user with Teddy.ai, DeltaHacks 2023", "https://i.ebayimg.com/images/g/vlIAAOSwikBcR0nA/s-l1200.jpg"))
    response = json.loads(response)
    try:
        url = response["transaction_details"]["blockExplorer"]
    except:
        url = "https://goerli.etherscan.io/token/0x791b1e3ba2088ecce017d1c60934804868691f67?a=0x0e5d299236647563649526cfa25c39d6848101f5"

    webbrowser.open_new(url)
    
    print("pic mf")

    return "Captured photo!"

def verify_quest_answer(answer: str, difficulty: str):
    print ("Quest difficulty level: " + difficulty)

    flow = 0
    if (str == "Easy"):
        flow = 1
    elif (str == "Medium"):
        flow = 2
    elif (str == "Hard"):
        flow = 3
    else:
        flow = 4

    if (answer == "yes"): 
        return "Sent " + str(flow) + " Flow tokens!"
    else:
        return "Your answer is wrong."

# Generate a response to the user's message - AI STUFF
def generate_response(message: str):
    st.session_state.chatMessages.append({"role": "user", "content": message})

    print(st.session_state.chatMessages)

    res = client.chat.completions.create(
        model="gpt-4",
        messages=st.session_state.chatMessages,
        stream=False,
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "send_money",
                    "description": "Send cryptocurrency to a specific person",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The name of the recipient."
                            },
                            "amount": {
                                "type": "string",
                                "description": "The amount of flow tokens that need to be sent."
                            }
                        }
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "take_photo",
                    "description": "Take a photo of the child",
                    "parameters": {}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "verify_quest_answer", 
                    "description": "Verifies the child's answer to a given 'quest' question. Called the moment an answer to a quest is given.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "answer": {
                                "type": "string",
                                "description": "A yes/no as to whether the given question was answered correctly."
                            },
                            "difficulty": {
                                "type": "string", 
                                "description": "The difficulty ('Easy'/'Medium'/'Hard'/'Demon') of the quest (question) relative to the child's level of learning."
                            }
                        }
                    }
                }
            }
        ],
    )

    # st.session_state.chatMessages.append(res.choices[0].message)
    calls = res.choices[0].message.tool_calls

    if (calls):
        availableFunctions = {
            "send_money": send_money,
            "take_photo": take_photo,
            "verify_quest_answer": verify_quest_answer,
        }

        for call in calls:
            functionCall = availableFunctions[call.function.name]
            functionArgs = json.loads(call.function.arguments)
            functionResponse = functionCall(**functionArgs)

            # st.session_state.chatMessages.append(
            #     {
            #         "tool_call_id": call.tool_call_id,
            #         "role": "function",
            #         "name": call.function.name,
            #         "content": functionResponse,
            #     }
            # )

            st.session_state.chatMessages.append({"role": "assistant", "content": functionResponse})

            secondRes = client.chat.completions.create(
                model="gpt-4",
                messages=st.session_state.chatMessages,
            )

            return functionResponse + " " + secondRes.choices[0].message.content
    else: 
        st.session_state.chatMessages.append(res.choices[0].message)
    
    print(res.choices[0].message.content)

    return res.choices[0].message.content

# Define the Streamlit app
def main():

    # st.title("start/stop buttons")
    # if st.button("Start"):
    #     print("stat button")
    # if st.button("Stop"):
    #     print("stop button")



    st.title("Welcome to Teddy.ai!")

    st.sidebar.title("Add Document Sources")
    st.session_state.additionalInfo = st.sidebar.text_input("Additional Info", key="moreInfo")

    # Sidebar to add document sources
    st.sidebar.title("Add Document Sources")
    sources = [
    ]
    source_title = st.sidebar.text_input("Source Title")
    source_url = st.sidebar.text_input("Source URL")

    if st.sidebar.button("Add Source") and source_title and source_url:
        sources.append({"title": source_title, "url": source_url})
        st.sidebar.success("Source added successfully!")
        getHTML(source_url)


    st.sidebar.write("Document Sources:")
    for source in sources:
        st.sidebar.write(f"- [{source['title']}]({source['url']})")

    # Chatbot interaction
    st.write("Chat with the Chatbot:")
    user_input = st.text_input("User:", "")
    if st.button("Send"):
        st.write("Chat:", user_input)
        response = generate_response(user_input)

        if ("photo" not in response.lower() and "flow" not in response.lower()):
            st.write(
                f"<div style='background-color:#f4f4f4;padding:10px;margin:10px;border-radius:5px;'>{response}</div>",
                unsafe_allow_html=True,
            )
            play_voice(response)

if __name__ == "__main__":
    main()

