# 🛡️ Zero-Trust PII Redaction Agent

[![Google Cloud Run](https://img.shields.io/badge/Deployed%20on-Cloud%20Run-blue?logo=google-cloud&logoColor=white)](https://pii-redactor-gateway-289826992892.us-central1.run.app)
[![Gemini 2.5 Flash](https://img.shields.io/badge/Powered%20by-Gemini%202.5%20Flash-orange?logo=google-gemini&logoColor=white)](https://deepmind.google/technologies/gemini/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **The Problem:** Enterprises are terrified of sending sensitive data (PII) to LLMs or third-party APIs.  
> **The Solution:** A high-speed, sequential AI agent that acts as a secure pre-processor, neutralizing PII before it ever leaves your infrastructure.

---

## 🚀 Live Endpoint
**API URL:** `https://pii-redactor-gateway-289826992892.us-central1.run.app/redact`  
**Method:** `POST`

---

## 🧠 How It Works (ADK Flex)
This agent uses the **Google Agent Development Kit (ADK)** and a **SequentialAgent** architecture to ensure maximum safety and accuracy.

1.  **Step 1: Identify 🔍**  
    The `PIIIdentifier` agent scans the raw text using Gemini 2.5 Flash to locate Names, Emails, Phone Numbers, Credit Cards, and Indian identifiers (Aadhaar/PAN).
2.  **Step 2: Redact & Validate 🛡️**  
    The `PIIRedactor` agent takes the findings, replaces them with unique placeholders (e.g., `[NAME_1]`), and generates a secure JSON map for audit purposes.

---

## 🏗️ Agent Architecture: Sequential Redaction Flow

The `pii_redactor_pro` gateway utilizes a sequential two-stage processing pipeline to ensure both high precision and absolute data neutrality:

<p align="center">
  <img src="https://raw.githubusercontent.com/DivyanshuJaiswal411/Gen-AI-Academy-APAC/main/Agent_Diagram.png" alt="PII Redactor Pro Sequential Agent Diagram" width="800">
  <br>
  <em>Figure 1: Sequential Agent Workflow for Zero-Trust Redaction</em>
</p>

1.  **PII Identifier (Deep Scan):** Gemini 2.5 Flash performs deep semantic reasoning on the input text to identify and categorize specific sensitive data entities (e.g., distinguishing between a generic Model ID and an Aadhaar number).
2.  **PII Redactor (Neutralization):** Once identified, the data is transformed in-memory using consistent placeholders (like `[NAME_1]`, `[ID_1]`) and a structural PII map is generated for the final validated JSON output.

---

## 🛠️ Technical Stack
- **AI Orchestration:** Google ADK (Agent Development Kit)
- **Model:** Gemini 2.5 Flash (Low latency, high context)
- **Framework:** FastAPI (Python 3.11)
- **Deployment:** Google Cloud Run (Serverless)
- **Governance:** Zero-Trust Architecture

---

## 📡 API Usage

### Request
```bash
curl -X POST "https://pii-redactor-gateway-289826992892.us-central1.run.app/redact" \
     -H "Content-Type: application/json" \
     -d '{"text": "My name is Divyanshu Jaiswal and my email is divyanshu@iitbhu.ac.in"}'
```

### Response
```json
{
  "redacted_text": "My name is [NAME_1] and my email is [EMAIL_1]",
  "pii_map": [
    {
      "category": "Name",
      "original_found": "Divyanshu Jaiswal",
      "placeholder": "[NAME_1]"
    },
    {
      "category": "Email Address",
      "original_found": "divyanshu@iitbhu.ac.in",
      "placeholder": "[EMAIL_1]"
    }
  ],
  "safety_score": 10
}
```

---

## 🏗️ Local Setup

1. **Clone the repo:**
   ```bash
   git clone https://github.com/DivyanshuJaiswal411/Gen-AI-Academy-APAC.git
   cd Gen-AI-Academy-APAC
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key
   GOOGLE_GENAI_USE_VERTEXAI=False
   ```

4. **Run the API:**
   ```bash
   uvicorn pii_agent.api:app --reload
   ```

---

## 🏆 Hackathon Submission: AI Governance 2026
This project proves that **Safe AI** is possible. By placing an intelligent, auditable redaction layer between users and LLMs, enterprises can finally embrace Generative AI without compromising data privacy.
