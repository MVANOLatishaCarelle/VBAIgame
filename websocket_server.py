# websocket_server.py
import os
from fastapi import FastAPI
from fastapi.websockets import WebSocket
import openai
import tempfile
import asyncio
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

class WebSocketManager:
    def __init__(self):
        self.connection_state = 'disconnected'
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5

@app.websocket("/ws/transcribe")
async def handle_audio_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive audio chunks from game client
            audio_data = await websocket.receive_bytes()

            # Save to temp file (OpenAI requires file upload)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
                tmp.write(audio_data)
                tmp.flush()

                # Send to OpenAI Whisper
                transcript = openai.Audio.transcribe(
                    file=open(tmp.name, "rb"),
                    model="whisper-1"
                )

            # Send text back via WebSocket
            await websocket.send_text(transcript["text"])

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)