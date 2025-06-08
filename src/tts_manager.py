"""
Text-to-Speech Manager for CoHost.AI.

This module provides optimized text-to-speech functionality using Google Cloud TTS
with audio caching, direct memory playback, and OBS integration for character
visibility management.

Author: Tom Pravetz
License: MIT
"""

import pyaudio
import wave
import os
import logging
import hashlib
import threading
import io
from typing import Optional, Dict

try:
    from google.cloud import texttospeech
except ImportError:
    raise ImportError(
        "google-cloud-texttospeech package not found. "
        "Please install it with: pip install google-cloud-texttospeech"
    )

from .OBSWebsocketsManager import OBSWebsocketsManager

logger = logging.getLogger(__name__)

class TTSManager:
    """
    Optimized Text-to-Speech Manager using Google Cloud TTS.

    Provides high-performance text-to-speech functionality with features including:
    - Google Cloud TTS integration
    - Audio response caching for improved performance
    - Direct memory audio playback (no temporary files)
    - OBS character visibility integration
    - Configurable audio device selection
    - Thread-safe operations

    Attributes:
        json_path: Path to Google Cloud service account JSON file
        device_index: PyAudio device index for audio output
        cache_enabled: Whether TTS response caching is enabled
        cache_size: Maximum number of cached audio responses
        buffer_size: Audio buffer size for playback optimization
        client: Google Cloud TTS client instance
        obs_manager: OBS WebSocket manager for character visibility
        audio_cache: Cache for storing generated audio data
        pyaudio_instance: PyAudio instance for audio playback
        cache_lock: Thread lock for cache operations
    """

    def __init__(
        self,
        json_path: str,
        device_index: int = 7,
        cache_enabled: bool = True,
        cache_size: int = 50,
        buffer_size: int = 4096
    ) -> None:
        """
        Initialize the TTS Manager.

        Args:
            json_path: Path to Google Cloud service account JSON file
            device_index: Audio device index for playback (default: 7)
            cache_enabled: Enable TTS response caching (default: True)
            cache_size: Maximum number of cached responses (default: 50)
            buffer_size: Audio buffer size for playback (default: 4096)

        Raises:
            FileNotFoundError: If Google Cloud credentials file doesn't exist
            ImportError: If required dependencies are missing
            Exception: If initialization of any component fails
        """
        self.json_path: str = json_path
        self.device_index: int = device_index
        self.cache_enabled: bool = cache_enabled
        self.cache_size: int = cache_size
        self.buffer_size: int = buffer_size

        # Initialize components
        self.client: Optional[texttospeech.TextToSpeechClient] = None
        self.obs_manager: Optional[OBSWebsocketsManager] = None
        self.audio_cache: Dict[str, bytes] = {}
        self.pyaudio_instance: Optional[pyaudio.PyAudio] = None
        self.cache_lock: threading.Lock = threading.Lock()

        # Initialize all components
        self._initialize_client()
        self._initialize_obs()
        self._initialize_audio()

    def _initialize_audio(self):
        """Initialize persistent PyAudio instance for better performance."""
        try:
            self.pyaudio_instance = pyaudio.PyAudio()

            # Validate the audio device
            self._validate_audio_device()

            logger.info("PyAudio instance initialized for optimized playback")
        except Exception as e:
            logger.error(f"Failed to initialize PyAudio: {e}")
            self.pyaudio_instance = None

    def _validate_audio_device(self):
        """Validate that the specified audio device exists and is usable."""
        if not self.pyaudio_instance:
            return

        try:
            device_count = self.pyaudio_instance.get_device_count()
            if self.device_index >= device_count:
                logger.error(f"Audio device index {self.device_index} is out of range (0-{device_count-1})")
                return

            device_info = self.pyaudio_instance.get_device_info_by_index(self.device_index)
            logger.info(f"Using audio device {self.device_index}: {device_info['name']}")
            logger.info(f"Device channels: {device_info['maxOutputChannels']}, Sample rate: {device_info['defaultSampleRate']}")

            if device_info['maxOutputChannels'] == 0:
                logger.error(f"Device {self.device_index} has no output channels!")

        except Exception as e:
            logger.error(f"Error validating audio device {self.device_index}: {e}")

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode('utf-8')).hexdigest()

    def _get_cached_audio(self, text: str) -> Optional[bytes]:
        """Get cached audio data if available."""
        if not self.cache_enabled:
            return None

        cache_key = self._get_cache_key(text)
        with self.cache_lock:
            return self.audio_cache.get(cache_key)

    def _cache_audio(self, text: str, audio_data: bytes):
        """Cache audio data."""
        if not self.cache_enabled:
            return

        cache_key = self._get_cache_key(text)
        with self.cache_lock:
            # Implement simple LRU by removing oldest if cache is full
            if len(self.audio_cache) >= self.cache_size:
                # Remove first (oldest) item
                oldest_key = next(iter(self.audio_cache))
                del self.audio_cache[oldest_key]

            self.audio_cache[cache_key] = audio_data
            logger.debug(f"Cached audio for text: {text[:50]}...")
        self._initialize_audio()

    def _initialize_client(self):
        """Initialize Google Cloud TTS client."""
        try:
            if not os.path.exists(self.json_path):
                raise FileNotFoundError(f"Google Cloud credentials file not found: {self.json_path}")

            self.client = texttospeech.TextToSpeechClient.from_service_account_file(self.json_path)
            logger.info("Google Cloud TTS client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS client: {e}")
            raise

    def _initialize_obs(self):
        """Initialize OBS WebSocket manager."""
        try:
            self.obs_manager = OBSWebsocketsManager()
            logger.info("OBS WebSocket manager initialized for TTS")
        except Exception as e:
            logger.warning(f"Failed to initialize OBS manager: {e}")
            # Don't raise here - TTS can work without OBS

    def synthesize_and_play(self, text: str, scene_name: str = "In-Game [OLD]",
                           bot_source: str = "AIBot", top_source: str = "AITop"):
        """
        Optimized synthesize text to speech and play it with OBS integration.
        Uses caching and parallel processing for better performance.

        Args:
            text: Text to synthesize
            scene_name: OBS scene name for character visibility
            bot_source: OBS source name for bot character
            top_source: OBS source name for top character
        """
        if not self.client:
            logger.error("TTS client not initialized")
            return

        try:
            # Check cache first
            audio_data = self._get_cached_audio(text)

            if audio_data:
                logger.debug(f"Using cached audio for: {text[:50]}...")
            else:
                logger.debug(f"Synthesizing new audio: {text[:50]}...")

                # Configure TTS request
                synthesis_input = texttospeech.SynthesisInput(text=text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    ssml_gender=texttospeech.SsmlVoiceGender.MALE
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16
                )

                # Generate speech
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )

                audio_data = response.audio_content
                self._cache_audio(text, audio_data)

            # Start OBS character visibility in parallel
            obs_thread = None
            if self.obs_manager:
                obs_thread = threading.Thread(
                    target=self._handle_obs_visibility,
                    args=(scene_name, bot_source, top_source, True),
                    daemon=True
                )
                obs_thread.start()

            # Play audio directly from memory
            self.play_audio_from_memory(audio_data)

            # Hide character in OBS
            if self.obs_manager:
                try:
                    self.obs_manager.set_source_visibility(scene_name, bot_source, False)
                    self.obs_manager.set_source_visibility(scene_name, top_source, False)
                except Exception as e:
                    logger.warning(f"Failed to hide character in OBS: {e}")

        except Exception as e:
            logger.error(f"Error in synthesize_and_play: {e}")

    def _handle_obs_visibility(self, scene_name: str, bot_source: str, top_source: str, visible: bool):
        """Handle OBS visibility changes in a separate thread."""
        try:
            self.obs_manager.set_source_visibility(scene_name, bot_source, visible)
            self.obs_manager.set_source_visibility(scene_name, top_source, visible)
        except Exception as e:
            logger.warning(f"Failed to set OBS visibility: {e}")

    def play_audio_from_memory(self, audio_data: bytes):
        """
        Play audio directly from memory without temporary files.

        Args:
            audio_data: Raw audio data to play
        """
        if not self.pyaudio_instance:
            logger.error("PyAudio not initialized")
            return

        try:
            # Parse the WAV data directly from memory
            audio_io = io.BytesIO(audio_data)

            # Use wave module to read from BytesIO
            wf = wave.open(audio_io, 'rb')

            # Open stream with optimized buffer size
            stream = self.pyaudio_instance.open(
                format=self.pyaudio_instance.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                output_device_index=self.device_index,
                frames_per_buffer=self.buffer_size
            )

            logger.info(f"Playing audio on device {self.device_index}: {wf.getnchannels()} channels, {wf.getframerate()} Hz")

            # Read and play data in optimized chunks
            data = wf.readframes(self.buffer_size)
            while data:
                stream.write(data)
                data = wf.readframes(self.buffer_size)

            logger.info("Audio playback completed successfully")

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
        finally:
            # Clean up resources
            try:
                if 'stream' in locals() and stream:
                    stream.stop_stream()
                    stream.close()
            except Exception as e:
                logger.warning(f"Error closing audio stream: {e}")

            try:
                if 'wf' in locals() and wf:
                    wf.close()
            except Exception as e:
                logger.warning(f"Error closing wave file: {e}")

            try:
                if 'audio_io' in locals() and audio_io:
                    audio_io.close()
            except Exception as e:
                logger.warning(f"Error closing audio IO: {e}")

    def _play_wave_file(self, file_path: str):
        """Optimized wave file playback."""
        wf = None
        stream = None

        try:
            wf = wave.open(file_path, 'rb')

            # Open stream with optimized buffer size
            stream = self.pyaudio_instance.open(
                format=self.pyaudio_instance.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True,
                output_device_index=self.device_index,
                frames_per_buffer=self.buffer_size
            )

            # Read and play data in optimized chunks
            data = wf.readframes(self.buffer_size)
            while data:
                stream.write(data)
                data = wf.readframes(self.buffer_size)

        except Exception as e:
            logger.error(f"Error playing audio: {e}")
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except Exception as e:
                    logger.warning(f"Error closing audio stream: {e}")

            if wf:
                try:
                    wf.close()
                except Exception as e:
                    logger.warning(f"Error closing wave file: {e}")

    def cleanup(self):
        """Clean up resources."""
        if self.pyaudio_instance:
            try:
                self.pyaudio_instance.terminate()
                logger.info("PyAudio instance terminated")
            except Exception as e:
                logger.warning(f"Error terminating PyAudio: {e}")

# Example usage
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tts_manager.py <path_to_google_credentials.json>")
        sys.exit(1)

    tts_manager = TTSManager(json_path=sys.argv[1])
    try:
        tts_manager.synthesize_and_play("Hello, this is a test of the optimized TTS system.")
    finally:
        tts_manager.cleanup()
