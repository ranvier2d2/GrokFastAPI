from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from pydantic import BaseModel
import xai_sdk
import logging
import os

app = FastAPI()
logger = logging.getLogger("uvicorn.error")
# Read the API key from the environment variable
API_KEY = os.getenv("XAI_API_KEY")
if not API_KEY:
	raise ValueError(
	    "API key not found. Please set the XAI_API_KEY environment variable.")

# Define the API key header
api_key_header = APIKeyHeader(name="X-API-Key")


def get_api_key(api_key_header: str = Security(api_key_header)):
	# if api_key_header == API_KEY:
		return api_key_header
	# else:
	# 	raise HTTPException(status_code=403, detail="Could not validate API key")


# Define the GrokClient class
class GrokClient:

	def __init__(self, api_key):
		self.client = xai_sdk.Client(api_key=api_key)
		self.chat = self.client.chat

	async def gpt_request(self,
	                      user_message,
	                      system_message=None,
	                      fun_mode=False):
		conversation = self.chat.create_conversation(fun_mode=fun_mode)
		if system_message:
			await conversation.add_response_no_stream(system_message)
		response = await conversation.add_response_no_stream(user_message)
		return response.message


# Initialize the GrokClient with the API key
grok_client = GrokClient(api_key=API_KEY)


class ChatRequest(BaseModel):
	message: str
	system_message: str = None
	fun_mode: bool = False


class ChatResponse(BaseModel):
	response: str


@app.post("/grok/chat/",
          response_model=ChatResponse,
          status_code=200,
          description="Chat with Grok and get a response.")
async def chat_with_grok(request: ChatRequest,
                         api_key: str = Depends(get_api_key)):
	try:
		logger.info(f"Received request with message length: {len(request.message)}")
		response_message = await grok_client.gpt_request(
						user_message=request.message,
						system_message=request.system_message,
						fun_mode=request.fun_mode)
		logger.info(f"Response message: {response_message}")
		return ChatResponse(response=response_message)
	except Exception as e:
		error_message = f"Error occurred: {str(e)}"
		logger.error(error_message)
		raise HTTPException(status_code=500, detail={"error": error_message})

# Define a root endpoint
@app.get("/")
async def read_root():
	return {"message": "Welcome to the FastAPI application"}


if __name__ == "__main__":
	import uvicorn
	uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
