# AI Agent Workflow Demo

This is a small experimental project exploring how an AI-driven workflow can be structured using Python and the OpenAI API.

The goal of this project was to simulate how an AI agent could process a business request through multiple stages instead of generating a single response directly.

---

## What this project does

The program accepts a business request from the user and processes it through several phases:

1. Planning – understand the intent of the request  
2. Execution – generate actionable content  
3. Review – refine clarity and professionalism  
4. Final Output – return the improved result

This structure mimics a simplified agent workflow often discussed in modern AI systems.

---

## Why I built this

I wanted to better understand:

- how to integrate OpenAI APIs into a Python application
- how to separate AI responsibilities into modular steps
- how agent-style workflows can be implemented without heavy frameworks

---

## Project Structure

ai-agent-workflow-demo/
│
├── main.py
├── agents/
│   └── worker.py
├── services/
│   └── openai_client.py
├── .env.example
└── README.md
---

## Setup

### 1. Clone repository

```bash
git clone <repo-url>
cd ai-agent-workflow-demo
2. Install dependencies
pip install -r requirements.txt
3. Configure API key

Create a .env file:

OPENAI_API_KEY=your_api_key_here

(API keys are not included for security reasons.)

Run the project
python main.py

Example input:

Create a marketing plan for a coffee shop
Notes

This project is intentionally lightweight and focuses on workflow design rather than building a full agent framework.

Possible Improvements

Streaming responses

Async task execution

Multiple agent roles (planner / reviewer)

Web interface

