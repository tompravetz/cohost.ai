"""
Configuration management for CoHost.AI.

This module provides centralized configuration management for the CoHost.AI
application, including environment variable handling, validation, and logging setup.

Author: Tom Pravetz
License: MIT
"""

import os
import logging
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """
    Setup logging configuration for the application.

    Configures both console and file logging with appropriate formatting.

    Args:
        level: Logging level as string (DEBUG, INFO, WARNING, ERROR).
               If None, reads from LOG_LEVEL environment variable.
               Defaults to INFO if not specified.

    Raises:
        ValueError: If an invalid logging level is provided.
    """
    log_level = level or os.getenv('LOG_LEVEL', 'INFO')

    # Convert string to logging level
    try:
        numeric_level = getattr(logging, log_level.upper())
    except AttributeError:
        raise ValueError(f"Invalid logging level: {log_level}")

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('voice_assistant.log', encoding='utf-8')
        ]
    )

class Config:
    """
    Configuration class for CoHost.AI.

    Manages all application configuration through environment variables
    with sensible defaults and validation.

    Attributes:
        google_credentials_path: Path to Google Cloud TTS credentials JSON file
        udp_port: Port for UDP broadcast listening
        obs_host: OBS WebSocket host address
        obs_port: OBS WebSocket port
        obs_password: OBS WebSocket password
        audio_device_index: PyAudio device index for TTS output
        mic_device_index: PyAudio device index for microphone input
        push_to_talk_start_key: Key to start recording
        push_to_talk_stop_key: Key to stop recording
        speech_recognition_language: Language code for speech recognition
        speech_recognition_timeout: Timeout for speech recognition in seconds
        obs_scene_name: OBS scene name for character visibility
        obs_bot_source: OBS source name for bot character
        obs_top_source: OBS source name for top character
        ollama_model: Ollama model name for AI responses
        enable_parallel_processing: Enable parallel processing optimizations
        tts_cache_enabled: Enable TTS response caching
        tts_cache_size: Maximum number of cached TTS responses
        audio_buffer_size: Audio buffer size for playback
        show_detailed_logs: Show detailed logs in CLI
        cli_refresh_rate: CLI refresh rate in seconds
        history_file: Path to conversation history file
    """

    def __init__(self) -> None:
        """
        Initialize configuration from environment variables.

        Raises:
            ValueError: If required configuration is missing or invalid
            FileNotFoundError: If Google credentials file doesn't exist
        """
        # Google Cloud TTS Configuration
        self.google_credentials_path: Optional[str] = os.getenv(
            'GOOGLE_CREDENTIALS_PATH'
        )

        # Network Configuration
        self.udp_port: int = int(os.getenv('UDP_PORT', '5005'))

        # OBS WebSocket Configuration
        self.obs_host: str = os.getenv('OBS_HOST', 'localhost')
        self.obs_port: int = int(os.getenv('OBS_PORT', '4455'))
        self.obs_password: str = os.getenv('OBS_PASSWORD', 'ZPpGrnxDm1pXYwgS')

        # Audio Device Configuration
        self.audio_device_index: int = int(os.getenv('AUDIO_DEVICE_INDEX', '7'))
        self.mic_device_index: int = int(os.getenv('MIC_DEVICE_INDEX', '-1'))

        # Speech Recognition Configuration
        self.push_to_talk_start_key: str = os.getenv(
            'PUSH_TO_TALK_START_KEY', 'F1'
        )
        self.push_to_talk_stop_key: str = os.getenv(
            'PUSH_TO_TALK_STOP_KEY', 'F2'
        )
        self.speech_recognition_language: str = os.getenv(
            'SPEECH_RECOGNITION_LANGUAGE', 'en-US'
        )
        self.speech_recognition_timeout: float = float(
            os.getenv('SPEECH_RECOGNITION_TIMEOUT', '5.0')
        )

        # OBS Scene and Source Configuration
        self.obs_scene_name: str = os.getenv('OBS_SCENE_NAME', 'In-Game [OLD]')
        self.obs_bot_source: str = os.getenv('OBS_BOT_SOURCE', 'AIBot')
        self.obs_top_source: str = os.getenv('OBS_TOP_SOURCE', 'AITop')

        # AI Model Configuration
        self.ollama_model: str = os.getenv('OLLAMA_MODEL', 'mistral')

        # Performance Configuration
        self.enable_parallel_processing: bool = (
            os.getenv('ENABLE_PARALLEL_PROCESSING', 'true').lower() == 'true'
        )
        self.tts_cache_enabled: bool = (
            os.getenv('TTS_CACHE_ENABLED', 'true').lower() == 'true'
        )
        self.tts_cache_size: int = int(os.getenv('TTS_CACHE_SIZE', '50'))
        self.audio_buffer_size: int = int(os.getenv('AUDIO_BUFFER_SIZE', '4096'))

        # User Interface Configuration
        self.show_detailed_logs: bool = (
            os.getenv('SHOW_DETAILED_LOGS', 'false').lower() == 'true'
        )
        self.cli_refresh_rate: float = float(os.getenv('CLI_REFRESH_RATE', '0.1'))

        # Data Storage Configuration
        self.history_file: str = os.getenv('HISTORY_FILE', 'cohost_history.json')

        # Validate configuration
        self._validate()
    
    def _validate(self) -> None:
        """
        Validate required configuration settings.

        Raises:
            ValueError: If required environment variables are missing
            FileNotFoundError: If required files don't exist
        """
        if not self.google_credentials_path:
            raise ValueError(
                "GOOGLE_CREDENTIALS_PATH environment variable is required. "
                "Please set it to the path of your Google Cloud credentials JSON file."
            )

        if not os.path.exists(self.google_credentials_path):
            raise FileNotFoundError(
                f"Google credentials file not found: {self.google_credentials_path}. "
                f"Please ensure the file exists and the path is correct."
            )

        # Validate port ranges
        if not (1 <= self.udp_port <= 65535):
            raise ValueError(f"UDP port must be between 1-65535, got: {self.udp_port}")

        if not (1 <= self.obs_port <= 65535):
            raise ValueError(f"OBS port must be between 1-65535, got: {self.obs_port}")

        # Validate audio configuration
        if self.audio_device_index < -1:
            raise ValueError(
                f"Audio device index must be >= -1, got: {self.audio_device_index}"
            )

        if self.mic_device_index < -1:
            raise ValueError(
                f"Microphone device index must be >= -1, got: {self.mic_device_index}"
            )

        # Validate performance settings
        if self.tts_cache_size < 1:
            raise ValueError(
                f"TTS cache size must be >= 1, got: {self.tts_cache_size}"
            )

        if self.audio_buffer_size < 512:
            raise ValueError(
                f"Audio buffer size must be >= 512, got: {self.audio_buffer_size}"
            )

        if self.cli_refresh_rate <= 0:
            raise ValueError(
                f"CLI refresh rate must be > 0, got: {self.cli_refresh_rate}"
            )

    def __repr__(self) -> str:
        """Return string representation of configuration."""
        return (
            f"Config(udp_port={self.udp_port}, obs_host='{self.obs_host}', "
            f"model='{self.ollama_model}', audio_device={self.audio_device_index})"
        )
