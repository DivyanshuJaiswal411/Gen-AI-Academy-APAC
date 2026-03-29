FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Cloud Run expects the app to listen on port 8080
EXPOSE 8080

# The ADK 'serve' command automatically finds 'root_agent' in agent.py
CMD ["uvicorn", "pii_agent.api:app", "--host", "0.0.0.0", "--port", "8080"]