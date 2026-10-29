from os import environ
from pathlib import Path

from dotenv import load_dotenv
from google import genai


build_working_directory = Path(environ['BUILD_WORKING_DIRECTORY'])
load_dotenv(build_working_directory / '.env')
gemini_api_key = environ['GEMINI_API_KEY']
gemini = genai.Client(api_key=gemini_api_key)
result = gemini.models.embed_content(model='gemini-embedding-2', contents='Hello, world!')
print(result.embeddings[0].values)
