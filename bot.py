import discord
from discord import app_commands
import requests
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class WebCrawler(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):

        await self.tree.sync()

client = WebCrawler()

@client.tree.command(name="define", description="Fetches the definition of a word.")
@app_commands.describe(word="The word you want to define.")
async def define(interaction: discord.Interaction, word: str):
    """Fetches definition from the dictionary API."""
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    
    if response.status_code == 200:
        data = response.json()
        definition = data[0]['meanings'][0]['definitions'][0]['definition']
        await interaction.response.send_message(f"**{word}**: {definition}")
    else:
        await interaction.response.send_message(f"Could not find a definition for **{word}**.")

@client.tree.command(name="chat", description="Chat with an AI.")
@app_commands.describe(message="Your message to the AI")
async def chat(interaction: discord.Interaction, message: str):
    await interaction.response.defer()

    shapes_client = OpenAI(
        api_key=os.getenv("CHAT_BOT_KEY"),
        base_url="https://api.shapes.inc/v1/",
    )

    try:
        response = shapes_client.chat.completions.create(
            model="shapesinc/aubin",
            messages=[{"role": "user", "content": message}]
        )

        reply = response.choices[0].message.content
        await interaction.followup.send(reply)

    except Exception as e:
        await interaction.followup.send(f"Error talking to AI: `{e}`")


client.run(os.getenv("BOT_TOKEN"))