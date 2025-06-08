"""
CoHost.AI - AI-Powered Streaming Co-Host.

A sophisticated AI streaming companion that provides real-time interaction
through voice recognition, AI responses, and text-to-speech synthesis.

Author: Tom Pravetz
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Tom Pravetz"
__license__ = "MIT"

# Main components
from .VoiceAssistant import VoiceAssistant
from .config import Config, setup_logging
from .AiManager import AiManager
from .tts_manager import TTSManager
from .OBSWebsocketsManager import OBSWebsocketsManager
from .SpeechRecognitionManager import SpeechRecognitionManager
from .cli_interface import CLIInterface

__all__ = [
    "VoiceAssistant",
    "Config",
    "setup_logging",
    "AiManager",
    "TTSManager",
    "OBSWebsocketsManager",
    "SpeechRecognitionManager",
    "CLIInterface",
]
