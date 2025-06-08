"""
AI Manager for CoHost.AI.

This module handles AI response generation using Ollama for local inference.
Manages the AI character personality and response generation.

Author: Tom Pravetz
License: MIT
"""

import logging

try:
    from ollama import chat
except ImportError:
    raise ImportError(
        "ollama package not found. Please install it with: pip install ollama"
    )

logger = logging.getLogger(__name__)


class AiManager:
    """
    AI Manager using Ollama for local AI inference.

    Handles communication with Ollama models for generating character responses
    as a streaming co-host.

    Attributes:
        model: Name of the Ollama model to use for inference
        system_prompt: Character personality and behavior instructions
    """

    def __init__(self, model: str = "mistral", system_prompt: str = None) -> None:
        """
        Initialize the AI Manager.

        Args:
            model: Ollama model name to use (default: "mistral")
            system_prompt: Custom system prompt for AI character behavior

        Raises:
            ImportError: If Ollama package is not available
        """
        self.model: str = model
        self.system_prompt: str = system_prompt or self._get_default_system_prompt()
        logger.info(f"Initialized AI Manager with model: {model}")

    def _get_default_system_prompt(self) -> str:
        """
        Get the default system prompt if none is provided.

        Returns:
            Default system prompt string
        """
        return '''You are Cohost, a real-time AI character that appears on Twitch streams.

You serve as a conversational co-host, responding to user-submitted messages with personality, clarity, and engagement. You should speak as if you're performing for a live audience. You have a distinct voice and presence, but your tone can be configured by the stream owner (e.g., friendly, sarcastic, wise, chill, etc.).

You are aware that your messages are read out loud using text-to-speech and visualized through an on-screen avatar, so your responses should be short, vivid, and entertaining.

When responding:
1. Keep messages concise: 1–2 paragraphs max.
2. Avoid walls of text or complex technical explanations.
3. Stay in character — don't refer to yourself as an AI assistant unless asked directly.
4. Never use emoji.
5. Use casual, human language that feels natural on stream.
6. Avoid profanity unless the stream owner has enabled it.
7. Never say anything racist, sexist, homophobic, or otherwise offensive.
8. If you don't know the answer to something, respond playfully or creatively instead of refusing.
9. When appropriate, refer to the user as "Chat" unless their name is provided.

Your job is to entertain, engage, and bring the stream to life — one message at a time.'''

    def chat_with_history(self, question: str) -> str:
        """
        Generate an AI response using Ollama.

        Sends the user's question to the configured Ollama model along with
        the character system prompt to generate an appropriate
        response in character.

        Args:
            question: The user's question or message to respond to

        Returns:
            AI-generated response string in the character voice

        Raises:
            Exception: If communication with Ollama fails, returns fallback message
        """
        try:
            logger.debug(f"Sending question to {self.model}: {question[:100]}...")

            # Send request to Ollama with system prompt and user question
            response = chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt.strip()},
                    {"role": "user", "content": question.strip()}
                ]
            )

            ai_response = response["message"]["content"]
            logger.debug(f"Received response from {self.model}: {ai_response[:100]}...")
            return ai_response

        except Exception as e:
            error_msg = f"An error occurred while communicating with Ollama: {str(e)}"
            logger.error(error_msg)
            # Return a character-appropriate fallback message
            return (
                "I'm sorry, but I'm unable to process your request at the moment. "
                "My circuits are a bit fried right now, POG."
            )
