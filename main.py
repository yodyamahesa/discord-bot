import discord
from dotenv import load_dotenv
import os
import google.generativeai as genai

from spire.doc import *
from spire.doc.common import *

import requests
from PIL import Image
import PIL.Image
from io import BytesIO
import urllib.parse
from urllib.parse import urlparse
import glob

from duckduckgo_search import DDGS

from rembg import remove

# Load environment variables from .env file
load_dotenv()

# Get Discord and API tokens from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_KEY = os.getenv("API_KEY")
genai.configure(api_key=API_KEY)

# Set up the generative model
generation_config = {
    "temperature": 0.5,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
model_name="gemini-pro",
generation_config=generation_config,
safety_settings=safety_settings,)

convo = model.start_chat(history=[])

# Create Discord client with intents
intents = discord.Intents.all()
bot = discord.Client(intents=intents)

# Event listener for when the bot is ready
@bot.event
async def on_ready():
    guild_count = len(bot.guilds)
    print(f"SampleDiscordBot is in {guild_count} guilds.")
    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")

# Event listener for new messages
@bot.event
async def on_message(message):
    if message.attachments:
        
        model = genai.GenerativeModel(
        model_name="gemini-pro-vision",
        generation_config=generation_config,
        safety_settings=safety_settings,)
        
        for attachment in message.attachments:
            try:
                image_url = attachment.url
                print(image_url)
                response = requests.get(image_url)
                img = Image.open(BytesIO(response.content))
                img = img.convert("RGB")
                img.save("local_image.jpg") 
            except: 
                await attachment.save("input." + os.path.splitext(attachment.filename)[1][1:])
        
    if message.content.startswith("GAMBARBOT"):
        
        model = genai.GenerativeModel(
        model_name="gemini-pro-vision",
        generation_config=generation_config,
        safety_settings=safety_settings,)
        imageAI = PIL.Image.open("local_image.jpg")
        
        bot_command = message.content[10:]
        response = model.generate_content([bot_command, imageAI], stream=True)
        response.resolve()
        await message.channel.send(response.text)
        
    if message.content.startswith("PDF"):
        
        # Search for files named "input" with any extension in the current directory
        file_path = glob.glob("input.*")

        # Check if any matching files are found
        if file_path:
            # Assuming you want to load the first matching file found
            # Create a Document object
            document = Document()
            # Load a Word DOCX file
            document.LoadFromFile(file_path[0])
            # Or load a Word DOC file
            #document.LoadFromFile("Sample.doc")

            # Create a ToPdfParameterList object
            parameters = ToPdfParameterList()
            

            # Create PDF bookmarks using Word bookmarks
            parameters.CreateWordBookmarks = True
            
            parameters.IsEmbeddedAllFonts = True
            
            # Or create PDF bookmarks using Word headings
            #parameters.CreateWordBookmarksUsingHeadings = True

            #Save the file to a PDF file
            document.SaveToFile("output.pdf", parameters)
            document.Close()
            
            with open("output.pdf", 'rb') as f:
                document = discord.File(f)
                await message.channel.send(file=document)
            
            
        
    if message.content.startswith("REMBG"):
        input_path = 'local_image.jpg'
        output_path = 'output.png'
        
        with open(input_path, 'rb') as i:
            with open(output_path, 'wb') as o:
                input = i.read()
                output = remove(input)
                o.write(output)
                
            with open('output.png', 'rb') as f:
                picture = discord.File(f)
                await message.channel.send(file=picture)

    if message.content.startswith("BOT"):
        
        model = genai.GenerativeModel(
        model_name="gemini-pro",
        generation_config=generation_config,
        safety_settings=safety_settings,)
                
        bot_command = message.content[4:]
        convo.send_message(bot_command)
        print(bot_command)
        await message.channel.send(convo.last.text)
        
    if message.content.startswith("SEARCHGAMBAR"):
        bot_command = message.content[13:]
        imageURL = {}
        
        with DDGS() as ddgs:
            keywords = bot_command
            ddgs_images_gen = ddgs.images(
            keywords,
            region="wt-wt",
            safesearch="off",
            size=None,
            # color="Monochrome",
            type_image=None,
            layout=None,
            license_image=None,
            max_results=2,
            )
            for r in ddgs_images_gen:
                imageURL = r
                image_url = imageURL.get('image', None)
                
                response = requests.get(image_url)
                if response.status_code == 200:
                    parsed_url = urlparse(image_url)
                    file_extension = os.path.splitext(parsed_url.path)[1]
                    filename = f"downloaded_image{file_extension}"
                    # Save the image to the local file
                    with open(filename, 'wb') as thefile:
                        thefile.write(response.content)
                        print(f"Image downloaded and saved as: {filename}")
                    with open(filename, 'rb') as f:
                        picture = discord.File(f)
                        await message.channel.send(file=picture)
                else:
                    print(f"Failed to download image. Status code: {response.status_code}")

# Run the bot with the specified Discord token
bot.run(DISCORD_TOKEN)