import requests
from app.core.logger import logger

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "phi3"


def ask_ai(question: str):
    logger.info(f"AI request received: {question}")

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL,
                "prompt": f"""
You are a warehouse management assistant.

Answer clearly and concisely.

User question: {question}
""",
                "stream": False
            }
        )

        result = response.json()
        answer = result.get("response", "No response from AI")

        logger.info("AI response generated successfully")

        return {
            "question": question,
            "answer": answer
        }

    except Exception as e:
        logger.error(f"Ollama AI failed: {str(e)}")

        return {
            "question": question,
            "answer": "AI service unavailable"
        }