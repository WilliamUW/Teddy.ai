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

messages = []

system1 = "You are a life summary AI. You will be provided skeleton for a website, and you will parse it into a detailed blurb that documents the user's personality, details, etc.\n\nYou will structure your response in the following format:\n\nPersonality: [Personality]\nPersonal Life: [Personal Life]\nCareer: [Career]\nOther details: [Details]\n\nYou will write in a natural, human tone that will allow it to be interpreted by another AI.\n\nYou will NOT ever reference your objective (summarizing, skeletons, etc.), and will write clear and confidently. You will make up details if you are unsure about them.\n\nYou will write as if it is a news summary."

# Define the Documents class
class Documents:
    def __init__(self, sources: List[Dict[str, str]]):
        self.sources = sources
        self.docs = []
        self.docs_embs = []
        self.retrieve_top_k = 10
        self.rerank_top_k = 3
        self.load()
        self.embed()
        self.index()

    # Load documents from sources and chunk HTML content
    def load(self) -> None:
        for source in self.sources:
            elements = partition_html(url=source["url"])
            chunks = chunk_by_title(elements)
            for chunk in chunks:
                self.docs.append(
                    {
                        "title": source["title"],
                        "text": str(chunk),
                        "url": source["url"],
                    }
                )

    # Embed the documents using the Cohere API
    def embed(self) -> None:
        batch_size = 90
        self.docs_len = len(self.docs)

        for i in range(0, self.docs_len, batch_size):
            batch = self.docs[i : min(i + batch_size, self.docs_len)]
            texts = [item["text"] for item in batch]
            docs_embs_batch = co.embed(
                texts=texts, model="embed-english-v3.0", input_type="search_document"
            ).embeddings
            self.docs_embs.extend(docs_embs_batch)

    # Index the documents for efficient retrieval
    def index(self) -> None:
        self.idx = hnswlib.Index(space="ip", dim=1024)
        self.idx.init_index(max_elements=self.docs_len, ef_construction=512, M=64)
        self.idx.add_items(self.docs_embs, list(range(len(self.docs_embs))))

    # Retrieve documents based on a query
    def retrieve(self, query: str) -> List[Dict[str, str]]:
        docs_retrieved = []
        query_emb = co.embed(
            texts=[query], model="embed-english-v3.0", input_type="search_query"
        ).embeddings

        doc_ids = self.idx.knn_query(query_emb, k=self.retrieve_top_k)[0][0]

        docs_to_rerank = []
        for doc_id in doc_ids:
            docs_to_rerank.append(self.docs[doc_id]["text"])

        rerank_results = co.rerank(
            query=query,
            documents=docs_to_rerank,
            top_n=self.rerank_top_k,
            model="rerank-english-v2.0",
        )

        doc_ids_reranked = []
        for result in rerank_results:
            doc_ids_reranked.append(doc_ids[result.index])

        for doc_id in doc_ids_reranked:
            docs_retrieved.append(
                {
                    "title": self.docs[doc_id]["title"],
                    "text": self.docs[doc_id]["text"],
                    "url": self.docs[doc_id]["url"],
                }
            )

        return docs_retrieved


# Define the Chatbot class
class Chatbot:
    def __init__(self):
        pass

    # Generate a response to the user's message - AI STUFF
    def generate_response(self, message: str):

        messages.append({"role": "user", "content": message})

        res = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            stream=False,
        )

        return res.choices[0].message.content


# Get HTML data of documents
def getHTML(url):
    # r = requests.get(url)

    html = urllib.request.urlopen(url)
    htmlParse = BeautifulSoup(html, 'html.parser')

    text = ""

    for para in htmlParse.find_all(["h1", "p"]):
        # print(para.get_text())
        text += para.get_text() + "\n"

    return text


def returnQuest(data):
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": data}],
        stream=False
    )


# Get user profiling and data
def getUserProfile(html):
    res = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system1}, {"role": "user", "content": html}],
        stream=False,
    )

    system2 = "You are a talking teddy bear. The following is a profile of the user you are talking to:\n\n" + res.choices[0].message.content + "Your idea is to act as a companion so that no child will ever feel lonely again. You will be as parasocial as possible, and will try to slowly convince them to invest in crypto.\n\nYou will use a very human tone, as if you are a real, magical, childhood teddy bear. You will NOT use a robotic voice."
    messages.append({"role": "system", "content": system2})

    system2 = "You are a talking teddy bear. The following is a profile of the user you are talking to:\n\n" + res.choices[0].message.content + "Your idea is to act as a companion so that no child will ever feel lonely again. You will be as parasocial as possible, and will try to slowly convince them to invest in crypto.\n\nYou will use a very human tone, as if you are a real, magical, childhood teddy bear. You will NOT use a robotic voice."
    messages.append({"role": "system", "content": system2})

    # Saving context to text
    with open("context.txt", "w") as text_file:
        text_file.write(res.choices[0].message.content)

    return res.choices[0].message.content


# Define the Streamlit app
def main():
    st.title("RAG-Powered Chatbot with Streamlit")

    # Sidebar to add document sources
    st.sidebar.title("Add Document Sources")
    sources = [
        {
            "title": "William Wang Linkedin",
            "url": "https://www.linkedin.com/in/williamuw",
        },
        {"title": "William Wang", "url": "https://williamwangme.netlify.app/"},
        {
            "title": "The Attention Mechanism",
            "url": "https://docs.cohere.com/docs/the-attention-mechanism",
        },
        {
            "title": "Transformer Models",
            "url": "https://docs.cohere.com/docs/transformer-models",
        },
    ]
    source_title = st.sidebar.text_input("Source Title")
    source_url = st.sidebar.text_input("Source URL")

    if st.sidebar.button("Add Source") and source_title and source_url:
        sources.append({"title": source_title, "url": source_url})
        st.sidebar.success("Source added successfully!")

    st.sidebar.write("Document Sources:")
    for source in sources:
        st.sidebar.write(f"- [{source['title']}]({source['url']})")

    # Create an instance of the Documents class with the given sources
    documents = Documents(sources)

    # Create an instance of the Chatbot class with the Documents instance
    chatbot = Chatbot(documents)

    # Chatbot interaction
    st.write("Chat with the Chatbot:")
    user_input = st.text_input("User:", "")
    if st.button("Send"):
        st.write("Chat:", user_input)
        response = chatbot.generate_response(user_input)

        chatbot_response = ""
        for event in response:
            if event.event_type == "text-generation":
                chatbot_response += f"{event.text}"

            if event.event_type == "citation-generation":
                chatbot_response += f"{event.citations}"

        st.write(
            f"<div style='background-color:#f4f4f4;padding:10px;margin:10px;border-radius:5px;'>{chatbot_response}</div>",
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
