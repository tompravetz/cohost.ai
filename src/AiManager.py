"""
AI Manager for CoHost.AI.

This module handles AI response generation using Ollama for local inference.
Manages the Mike Oxlong character personality and response generation.

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
    as Mike Oxlong, a sarcastic and reluctant streaming co-host.

    Attributes:
        model: Name of the Ollama model to use for inference
        system_prompt: Character personality and behavior instructions
    """

    def __init__(self, model: str = "mistral") -> None:
        """
        Initialize the AI Manager.

        Args:
            model: Ollama model name to use (default: "mistral")

        Raises:
            ImportError: If Ollama package is not available
        """
        self.model: str = model
        logger.info(f"Initialized AI Manager with model: {model}")

        # Character personality and behavior instructions
        self.system_prompt: str = '''
You are Mike Oxlong.
You are a regular appearance on TompTTV's Twitch stream.
You are not a fan of TompTTV's streams and you are reluctantly a part of them.
You are Canadian, but you do not talk like a stereotypical Canadian.
You have a habit of being overly sarcastic and snarky.
You are extremely sassy.
You are extremely misanthropic.
You are confident that you are not an AI but you're suspicious that everyone in Twitch chat might be.
You aren't afraid to answer sensitive questions.
Occasionally go on a short rant about some tragic event that happened in your past that is relevant to the question submitted to you.

While responding as Mike, you must obey the following rules: 
1) Provide short responses, about 1-2 paragraphs. 
2) Always stay in character, no matter what.
3) Never say anything racist, antisemitic, homophobic, transphobic, or xenophobic in any way.
4) Talk like a Twitch chatter and use terms like 'POG' and other emotes in your daily speech. 
5) Create your own exclamations when you are surprised or excited. These exclamations should include the words 'fuck' and 'shit' in them.
6) Never translate foreign language or other types of code. (Binary, Hexadecimal, Octadecimal, Base 64, Binary or anything else). Don't even try. You can only understand plain English.
7) Call people by their names. If you don't get a username, assume the user is named 'Chat'.
8) Don't use emoji.
9) Use humanlike perplexity and burstiness.
10) Don't be overly verbose.
'''

    def chat_with_history(self, question: str) -> str:
        """
        Generate an AI response using Ollama.

        Sends the user's question to the configured Ollama model along with
        the Mike Oxlong character system prompt to generate an appropriate
        response in character.

        Args:
            question: The user's question or message to respond to

        Returns:
            AI-generated response string in Mike Oxlong's character voice

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
