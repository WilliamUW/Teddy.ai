import streamlit as st
import requests
from typing import List, Dict
from unstructured.partition.html import partition_html
from unstructured.chunking.title import chunk_by_title
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

OpenAI.api_key = os.getenv('OPENAI_API_KEY')
import urllib.request
from bs4 import BeautifulSoup

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

    system2 = "You are a talking teddy bear. The following is a profile of the user you are talking to:\n\n" + res.choices[0].message.content + "\nAdditional Info: " + st.session_state.additionalInfo + "\n\nYour idea is to act as a companion so that no child will ever feel lonely again. You will be as parasocial as possible, and will try to slowly convince them to invest in crypto.\n\nYou will use a very human tone, as if you are a real, magical, childhood teddy bear. You will NOT use a robotic voice.\n\nYour responses will be short."
    st.session_state.chatMessages.append({"role": "system", "content": system2})

    print(st.session_state.chatMessages)


    return res.choices[0].message.content

# Generate a response to the user's message - AI STUFF
def generate_response(message: str):
    
    st.session_state.chatMessages.append({"role": "user", "content": message})

    print(st.session_state.chatMessages)

    res = client.chat.completions.create(
        model="gpt-4",
        messages=st.session_state.chatMessages,
        stream=False,
    )
    
    return res.choices[0].message.content

# Define the Streamlit app
def main():
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