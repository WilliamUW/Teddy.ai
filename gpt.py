import asyncio
import openai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve API key from .env file
openai.api_key = os.getenv('OPENAI_API_KEY')

# Context for the Teddy.ai chatbot
teddy_context = """
Teddy.ai is a teddy bear chatbot that knows everything about its owner. The owner has uploaded the following information:
- Name: Alice
- Favorite hobbies: Reading, painting, and hiking
- Favorite music: Classical and Jazz
- Profession: Software Developer
- Pets: A dog named Sparky
"""

async def chat():
    while(1):
        user_input = input('input: ')
        
        # Combining user input with the context
        prompt = user_input

        # Using OpenAI GPT-3.5 Turbo model for response generation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "system", "content": "You are Teddy.ai, a teddy bear chatbot." + teddy_context},
                {"role": "user", "content": user_input}
            ]
        )

        # Optionally, use Cohere's RAG for additional information retrieval if needed
        # cohere_response = cohere_client.generate(...)

        print(response.choices[0].message['content'])

asyncio.run(chat())
