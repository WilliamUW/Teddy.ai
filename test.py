import urllib.request
from bs4 import BeautifulSoup
import openai
import os
from openai import OpenAI
import dotenv
dotenv.load_dotenv(".env")


url = "https://github.com/stampixel?tab=repositories"
html = urllib.request.urlopen(url)
htmlParse = BeautifulSoup(html, 'html.parser')

# getting all the paragraphs
for para in htmlParse.find_all(["h1", "b", "p", "h2"]):
    print(para.get_text())

# print(htmlParse.get_text())

with open("context.txt", "w") as text_file:
    text_file.write(htmlParse.get_text())


# import requests
# data = requests.get("https://github.com/stampixel?tab=repositories")
# print(data.text)

#
#
# def getHTML(url):
#     data = requests.get(url)
#     print(data.text)
#
#     data = data.text
#
#     # question = data['content']
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "system", "content": """
#
#         translate text in to british
#
#     """}, {"role": "user", "content": """
#
#         hell my name is kevin
#
#     """}],
#         max_tokens=128,
#         temperature=0.3,
#         top_p=1
#     )
#
#     # print(response)
#     content = response["choices"][0]["message"]["content"]
#     print(content)
#
#     with open("context.txt", "w") as text_file:
#         text_file.write(content)
#     return {"data": content}
#
#
# getHTML("https://github.com/")