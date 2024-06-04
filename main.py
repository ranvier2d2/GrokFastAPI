from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import xai_sdk
import os

app = FastAPI()

# Read the API key from the environment variable
API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
		raise ValueError("API key not found. Please set the XAI_API_KEY environment variable.")

# Define the API key header
api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key_header: str = Security(api_key_header)):
		if api_key_header == API_KEY:
				return api_key_header
		else:
				raise HTTPException(
						status_code=403,
						detail="Could not validate API key"
				)

# Initialize the xai_sdk client with the API key
client = xai_sdk.Client(api_key=API_KEY)
chat = client.chat

class ChatRequest(BaseModel):
		message: str

class ChatResponse(BaseModel):
		response: str

@app.post("/grok/chat/", response_model=ChatResponse, status_code=200, description="Chat with Grok and get a response.")
async def chat_with_grok(request: ChatRequest, api_key: str = Depends(get_api_key)):
		try:
				conversation = chat.create_conversation()
				response = await conversation.add_response_no_stream(request.message)
				return ChatResponse(response=response.message)
		except Exception as e:
				raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
		import uvicorn
		uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
