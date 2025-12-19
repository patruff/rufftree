"""
Vercel Serverless Function for Real-time RAG Queries
Endpoint: /api/query
"""
import os
import json
from http.server import BaseHTTPRequestHandler
from google import genai


def get_client():
    """Initialize Google GenAI client."""
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_GENAI_API_KEY environment variable not set")
    return genai.Client(api_key=api_key)


def get_store_name():
    """Get the rufftree File Search store name."""
    # Hardcode the known store name to avoid listing overhead
    # This is the existing rufftree store
    return os.getenv("RUFFTREE_STORE_NAME", "fileSearchStores/rufftreefamilydocuments-nrf1ymofronp")


def query_documents(client, store_name, query, model="gemini-2.5-flash"):
    """
    Query the documents using RAG with citations.
    Returns tuple of (answer, citations_list)
    """
    # Use the file search store as a tool in generation call
    file_search_config = {
        'file_search_store_names': [store_name]
    }

    response = client.models.generate_content(
        model=model,
        contents=query,
        config={
            'tools': [{
                'file_search': file_search_config
            }]
        }
    )

    # Extract answer
    answer = response.text

    # Extract citations from grounding metadata
    citations = []
    if response.candidates and len(response.candidates) > 0:
        grounding = response.candidates[0].grounding_metadata
        if grounding and grounding.grounding_chunks:
            for chunk in grounding.grounding_chunks:
                if chunk.retrieved_context:
                    citations.append({
                        "title": chunk.retrieved_context.title,
                        "uri": getattr(chunk.retrieved_context, 'uri', 'N/A')
                    })

    # Deduplicate citations by title
    unique_citations = []
    seen_titles = set()
    for citation in citations:
        if citation['title'] not in seen_titles:
            seen_titles.add(citation['title'])
            unique_citations.append(citation['title'])

    return answer, unique_citations


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""

    def _set_cors_headers(self):
        """Set CORS headers to allow requests from GitHub Pages."""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        """Handle preflight CORS requests."""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_POST(self):
        """Handle POST requests with query."""
        try:
            # Read request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            request_data = json.loads(post_data.decode('utf-8'))

            # Extract query from request
            query = request_data.get('query', '').strip()
            if not query:
                self.send_response(400)
                self._set_cors_headers()
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Query parameter is required'
                }).encode())
                return

            # Optional: get asker name
            asker_name = request_data.get('name', 'Anonymous')

            # Initialize client and run query
            client = get_client()
            store_name = get_store_name()

            answer, citations = query_documents(client, store_name, query)

            # Return response
            self.send_response(200)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            response_data = {
                'success': True,
                'answer': answer,
                'citations': citations,
                'asker': asker_name,
                'timestamp': None  # Will be set by client
            }

            self.wfile.write(json.dumps(response_data).encode())

        except Exception as e:
            # Return error response
            self.send_response(500)
            self._set_cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            error_response = {
                'success': False,
                'error': str(e)
            }

            self.wfile.write(json.dumps(error_response).encode())

    def do_GET(self):
        """Handle GET requests - return API info."""
        self.send_response(200)
        self._set_cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        info = {
            'name': 'Rufftree Query API',
            'version': '1.0.0',
            'usage': 'POST with JSON body: {"query": "your question", "name": "optional name"}'
        }

        self.wfile.write(json.dumps(info).encode())
