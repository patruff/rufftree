#!/usr/bin/env python3
"""
FastAPI server for Grok Voice Agent with family history RAG integration.
Proxies WebSocket connections between browser and Grok, handling RAG queries server-side.
"""
import os
import json
import asyncio
import base64
from typing import Optional
import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from google import genai

# Environment variables
XAI_API_KEY = os.getenv("XAI_API_KEY")
GOOGLE_GENAI_API_KEY = os.getenv("GOOGLE_GENAI_API_KEY")
RUFFTREE_STORE_NAME = os.getenv("RUFFTREE_STORE_NAME", "fileSearchStores/rufftreefamilydocuments-nrf1ymofronp")

app = FastAPI(title="Rufftree Voice Agent")

# Serve static files (HTML, etc.)
app.mount("/static", StaticFiles(directory="."), name="static")


def get_genai_client():
    """Initialize Google GenAI client for RAG queries."""
    if not GOOGLE_GENAI_API_KEY:
        raise ValueError("GOOGLE_GENAI_API_KEY not set")
    return genai.Client(api_key=GOOGLE_GENAI_API_KEY)


def query_family_documents(question: str, max_results: int = 5) -> dict:
    """
    Query family documents using Google GenAI RAG.
    Returns answer with citations.
    """
    try:
        client = get_genai_client()

        # Use the file search store
        file_search_config = {
            'file_search_store_names': [RUFFTREE_STORE_NAME]
        }

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question,
            config={
                'tools': [{
                    'file_search': file_search_config
                }]
            }
        )

        # Extract answer
        answer = response.text

        # Extract citations
        citations = []
        if response.candidates and len(response.candidates) > 0:
            grounding = response.candidates[0].grounding_metadata
            if grounding and grounding.grounding_chunks:
                for chunk in grounding.grounding_chunks:
                    if chunk.retrieved_context:
                        citations.append(chunk.retrieved_context.title)

        # Deduplicate citations
        unique_citations = list(dict.fromkeys(citations))

        return {
            "status": "success",
            "answer": answer,
            "citations": unique_citations[:max_results]
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "answer": f"I encountered an error searching the family documents: {str(e)}"
        }


async def handle_grok_function_call(ws_grok, event):
    """
    Handle function calls from Grok Voice Agent.
    Execute RAG query and send result back.
    """
    function_name = event.get("name")
    call_id = event.get("call_id")
    arguments = json.loads(event.get("arguments", "{}"))

    print(f"🔧 Function called: {function_name}")
    print(f"   Arguments: {arguments}")

    if function_name == "query_family_history":
        question = arguments.get("question", "")
        print(f"   Querying: {question}")

        # Execute RAG query
        result = query_family_documents(question)

        # Format response for voice
        if result["status"] == "success":
            answer = result["answer"]
            if result["citations"]:
                answer += f"\n\nSources: {', '.join(result['citations'])}"
        else:
            answer = result["answer"]

        # Send function result back to Grok
        await ws_grok.send(json.dumps({
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": call_id,
                "output": answer
            }
        }))

        # Request Grok to continue
        await ws_grok.send(json.dumps({
            "type": "response.create",
            "response": {
                "modalities": ["text", "audio"]
            }
        }))

        print(f"   ✅ RAG query completed, result sent to Grok")
    else:
        print(f"   ⚠️  Unknown function: {function_name}")


async def proxy_client_to_grok(ws_client: WebSocket, ws_grok):
    """Forward messages from browser client to Grok."""
    try:
        while True:
            # Receive from browser
            message = await ws_client.receive_text()

            # Forward to Grok
            await ws_grok.send(message)

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in client->grok proxy: {e}")


async def proxy_grok_to_client(ws_client: WebSocket, ws_grok):
    """Forward messages from Grok to browser client, handling function calls."""
    try:
        while True:
            # Receive from Grok
            message = await ws_grok.recv()
            event = json.loads(message)

            event_type = event.get("type")

            # Handle function calls server-side (don't send to client)
            if event_type == "response.function_call_arguments.done":
                print(f"📞 Intercepting function call from Grok")
                await handle_grok_function_call(ws_grok, event)
                continue

            # Forward all other events to client
            await ws_client.send_text(message)

            # Log important events
            if event_type == "response.output_audio_transcript.delta":
                delta = event.get("delta", "")
                if delta:
                    print(f"🗣️  Grok: {delta}", end="", flush=True)
            elif event_type == "response.output_audio_transcript.done":
                print()  # New line after transcript completes

    except websockets.exceptions.ConnectionClosed:
        print("Grok connection closed")
        await ws_client.close()
    except Exception as e:
        print(f"Error in grok->client proxy: {e}")
        await ws_client.close()


@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """
    WebSocket endpoint that proxies between browser and Grok Voice Agent API.
    Handles RAG function calls server-side.
    """
    await websocket.accept()
    print("✅ Client connected to voice WebSocket")

    # Check for required API keys
    if not XAI_API_KEY:
        error_msg = (
            "XAI_API_KEY not configured on server. "
            "Set secrets in GitHub (Settings → Secrets → Actions) or via Fly CLI: "
            "fly secrets set XAI_API_KEY=your-key"
        )
        print(f"❌ {error_msg}")
        await websocket.send_json({
            "type": "error",
            "error": error_msg
        })
        await websocket.close()
        return

    if not GOOGLE_GENAI_API_KEY:
        error_msg = (
            "GOOGLE_GENAI_API_KEY not configured on server. "
            "Set secrets in GitHub or via Fly CLI: "
            "fly secrets set GOOGLE_GENAI_API_KEY=your-key"
        )
        print(f"❌ {error_msg}")
        await websocket.send_json({
            "type": "error",
            "error": error_msg
        })
        await websocket.close()
        return

    try:
        # Connect to Grok Voice Agent API
        grok_url = "wss://api.x.ai/v1/realtime"

        print(f"🔌 Connecting to Grok Voice Agent API at {grok_url}...")
        async with websockets.connect(
            uri=grok_url,
            ssl=True,
            additional_headers={"Authorization": f"Bearer {XAI_API_KEY}"}
        ) as ws_grok:
            print("✅ Connected to Grok")

            # Configure Grok session with RAG function tool
            session_config = {
                "type": "session.update",
                "session": {
                    "voice": "Ara",
                    "instructions": (
                        "You are a knowledgeable family history assistant for the Ruff family. "
                        "When users ask questions about family history, people, events, or stories, "
                        "use the query_family_history function to search through family documents. "
                        "Provide warm, conversational answers and mention your sources. "
                        "If you don't find information in the documents, say so honestly."
                    ),
                    "turn_detection": {"type": "server_vad"},
                    "audio": {
                        "input": {"format": {"type": "audio/pcm", "rate": 24000}},
                        "output": {"format": {"type": "audio/pcm", "rate": 24000}}
                    },
                    "tools": [
                        {
                            "type": "function",
                            "name": "query_family_history",
                            "description": (
                                "Search through Ruff family documents, stories, and records to answer "
                                "questions about family history, genealogy, people, events, and stories. "
                                "Use this whenever the user asks about the family."
                            ),
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "question": {
                                        "type": "string",
                                        "description": "The question to search for in family documents"
                                    }
                                },
                                "required": ["question"]
                            }
                        }
                    ]
                }
            }

            await ws_grok.send(json.dumps(session_config))
            print("✅ Grok session configured with RAG tool")

            # Notify client that connection is ready
            await websocket.send_json({
                "type": "connection.ready",
                "message": "Voice agent connected and ready"
            })

            # Start bidirectional proxy
            await asyncio.gather(
                proxy_client_to_grok(websocket, ws_grok),
                proxy_grok_to_client(websocket, ws_grok)
            )

    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        await websocket.send_json({
            "error": str(e)
        })
        await websocket.close()


@app.get("/")
async def root():
    """Serve the main voice interface page."""
    return FileResponse("voice_query.html")


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "xai_configured": bool(XAI_API_KEY),
        "genai_configured": bool(GOOGLE_GENAI_API_KEY)
    }


if __name__ == "__main__":
    import uvicorn

    print("\n🎤 Starting Rufftree Voice Agent Server")
    print("=" * 50)

    # Check required environment variables with detailed messages
    missing_vars = []

    if not XAI_API_KEY:
        print("❌ ERROR: XAI_API_KEY not set")
        print("   Get API key from: https://console.x.ai")
        print("   Set with: fly secrets set XAI_API_KEY=your-key")
        missing_vars.append("XAI_API_KEY")
    else:
        print(f"✅ XAI_API_KEY configured ({XAI_API_KEY[:10]}...)")

    if not GOOGLE_GENAI_API_KEY:
        print("❌ ERROR: GOOGLE_GENAI_API_KEY not set")
        print("   Get API key from: https://aistudio.google.com/apikey")
        print("   Set with: fly secrets set GOOGLE_GENAI_API_KEY=your-key")
        missing_vars.append("GOOGLE_GENAI_API_KEY")
    else:
        print(f"✅ GOOGLE_GENAI_API_KEY configured ({GOOGLE_GENAI_API_KEY[:10]}...)")

    print(f"✅ RUFFTREE_STORE_NAME: {RUFFTREE_STORE_NAME}")

    if missing_vars:
        print("\n⚠️  WARNING: Server starting but voice features will not work!")
        print(f"   Missing variables: {', '.join(missing_vars)}")
        print("   WebSocket connections will fail until secrets are set.")
        print("\n   To fix:")
        print("   1. Add secrets to GitHub: Settings → Secrets → Actions")
        print("   2. Or set via Fly CLI: fly secrets set KEY=value")
        print("   3. Redeploy to apply changes")
    else:
        print("\n✅ All environment variables configured correctly!")

    print("\n" + "=" * 50)
    print("Voice interface: http://localhost:8000")
    print("Health check: http://localhost:8000/health")
    print("=" * 50 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
