FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY voice_server.py .
COPY voice_query.html .
COPY queries.html .
COPY index.html .
COPY graph.html .
COPY submit_story.html .
COPY person_generator.html .
COPY easy_add.html .
COPY export_minitree.html .
COPY thank_you.html .
COPY stored_queries.json .
COPY family_tree.json .

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "voice_server.py"]
