from google import genai
from dotenv import load_dotenv

load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="You are an autonomous monitoring agent for Nigeria's pharmaceutical supply chain. Given a continuous stream of movement events (IMPORT, TRANSFER, DISPENSE) with batch IDs, locations, timestamps, and quantities:List 3 concrete risk signals that would indicate a possible counterfeit medication. For each signal, explain the logic in one sentence",
)
# print(response.text)
