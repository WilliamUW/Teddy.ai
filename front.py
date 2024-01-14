import streamlit as st
import requests
from typing import List, Dict
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
from helpers.camera import capture_photo
import webbrowser
import asyncio
from helpers.verbwire import mintNFT
import urllib.request
from bs4 import BeautifulSoup

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
    # r = requests.get(url)

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
    print("choice 1")
    if "additionalInfo" not in st.session_state:
        st.session_state.additionalInfo = ""
    system2 = "You are a talking teddy bear. The following is a profile of the user you are talking to:\n\n" + res.choices[0].message.content + "\nAdditional Info: " + st.session_state.additionalInfo + "\n\nYour idea is to act as a companion so that no child will ever feel lonely again. You will be as parasocial as possible.\n\nYou will use a very human tone, as if you are a real, magical, childhood teddy bear. You will NOT use a robotic voice.\n\nYour responses will be short."
    print("choice 2")
    st.session_state.chatMessages.append({"role": "system", "content": system2})
    print("choice 3")
    print(st.session_state.chatMessages)
    print("choice 4")

    return res.choices[0].message.content

def send_money(name: str, amount: str):
    flow_util.open_transaction_page(name, int(amount))
    print("worked")

def take_photo():
    print("Initiating capture... wait for camera to load.")

    capture_photo()
    response = asyncio.run(mintNFT("Teddy Bear #1", "Memory of user with Teddy.ai, DeltaHacks 2023", "https://i.ebayimg.com/images/g/vlIAAOSwikBcR0nA/s-l1200.jpg"))
    response = json.loads(response)
    try:
        url = response["transaction_details"]["blockExplorer"]
    except:
        url = "https://goerli.etherscan.io/token/0x791b1e3ba2088ecce017d1c60934804868691f67?a=0x0e5d299236647563649526cfa25c39d6848101f5"

    webbrowser.open_new(url)

    print("pic mf")

    return response.json()

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
            }
        ],
    )

    calls = res.choices[0].message.tool_calls

    if (calls):
        availableFunctions = {
            "send_money": send_money,
            "take_photo": take_photo,
        }
        st.session_state.chatMessages.append(res.choices[0].message)

        for call in calls:
            functionCall = availableFunctions[call.function.name]
            functionArgs = json.loads(call.function.arguments)
            functionResponse = functionCall(**functionArgs)

            st.session_state.chatMessages.append(
                {
                    "tool_call_id": call.id,
                    "role": "function",
                    "name": call.function.name,
                    "content": functionResponse,
                }
            )

            secondRes = client.chat.completions.create(
                model="gpt-4",
                messages=st.session_state.chatMessages,
            )

            return secondRes.choices[0].message.content
    print(res.choices[0].message.content)
    return res.choices[0].message.content

# Define the Streamlit app
def main():

    st.title("RAG-Powered Chatbot with Streamlit")
    if st.button("Start"):
        print("stat button")
    if st.button("Stop"):
        print("stop button")



    st.title("RAG-Powered Chatbot with Streamlit")

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

        st.write(
            f"<div style='background-color:#f4f4f4;padding:10px;margin:10px;border-radius:5px;'>{response}</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()

