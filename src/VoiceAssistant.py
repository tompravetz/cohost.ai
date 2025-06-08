"""
Main Voice Assistant module for CoHost.AI.

This module contains the core VoiceAssistant class that orchestrates all
components of the CoHost.AI system including AI responses, TTS, speech
recognition, and OBS integration.

Author: Tom Pravetz
License: MIT
"""

import json
import os
import socket
import threading
import queue
import logging
import time
from typing import Optional, List, Dict, Any

from rich.console import Console

from .config import Config
from .AiManager import AiManager
from .OBSWebsocketsManager import OBSWebsocketsManager
from .tts_manager import TTSManager
from .SpeechRecognitionManager import SpeechRecognitionManager
from .cli_interface import CLIInterface

logger = logging.getLogger(__name__)
console = Console()

class VoiceAssistant:
    """
    Main Voice Assistant class for CoHost.AI.

    Orchestrates all components including AI responses, text-to-speech,
    speech recognition, OBS integration, and UDP communication.

    This class serves as the central coordinator for the entire CoHost.AI
    system, managing the flow of data between different components and
    providing a unified interface for the streaming co-host functionality.

    Attributes:
        config: Application configuration
        history: Conversation history
        processed_questions: Set of already processed questions
        question_queue: Queue for incoming questions
        udp_socket: UDP socket for broadcast listening
        running: Flag indicating if the assistant is running
        cli: Command-line interface
        ai_manager: AI response generation manager
        obs_manager: OBS WebSocket integration manager
        tts_manager: Text-to-speech manager
        speech_manager: Speech recognition manager
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Initialize the Voice Assistant.

        Args:
            config: Configuration object. If None, creates from environment.

        Raises:
            ValueError: If configuration is invalid
            FileNotFoundError: If required files are missing
            ImportError: If required dependencies are missing
        """
        self.config: Config = config or Config()
        self.history: List[Dict[str, str]] = self.load_history()
        self.processed_questions: set = set()
        self.question_queue: queue.Queue = queue.Queue()
        self.udp_socket: Optional[socket.socket] = None
        self.running: bool = False

        # Initialize CLI interface
        self.cli: CLIInterface = CLIInterface(
            show_detailed_logs=self.config.show_detailed_logs,
            refresh_rate=self.config.cli_refresh_rate
        )

        # Initialize managers
        try:
            self.ai_manager = AiManager(model=self.config.ollama_model)
            self.obs_manager = OBSWebsocketsManager(
                host=self.config.obs_host,
                port=self.config.obs_port,
                password=self.config.obs_password
            )
            self.tts_manager = TTSManager(
                json_path=self.config.google_credentials_path,
                device_index=self.config.audio_device_index,
                cache_enabled=self.config.tts_cache_enabled,
                cache_size=self.config.tts_cache_size,
                buffer_size=self.config.audio_buffer_size
            )

            # Initialize speech recognition manager
            self.speech_manager = SpeechRecognitionManager(
                mic_device_index=self.config.mic_device_index,
                start_key=self.config.push_to_talk_start_key,
                stop_key=self.config.push_to_talk_stop_key,
                language=self.config.speech_recognition_language,
                timeout=self.config.speech_recognition_timeout,
                on_speech_callback=self._on_speech_recognized
            )

            # Set up CLI callback for speech recognition
            self.speech_manager.set_cli_callback(self._on_speech_event)

            logger.info("All managers initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize managers: {e}")
            raise

    def setup_udp_listener(self):
        """Set up UDP socket for listening to broadcasts."""
        try:
            self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.udp_socket.bind(('', self.config.udp_port))
            logger.info(f"UDP socket bound to port {self.config.udp_port}")
        except Exception as e:
            logger.error(f"Failed to setup UDP listener: {e}")
            raise

    def udp_listener(self):
        """Listen for UDP broadcasts and queue questions."""
        console.print(f"[green]Listening for UDP broadcasts on port {self.config.udp_port}")
        logger.info(f"Started UDP listener on port {self.config.udp_port}")

        while self.running:
            try:
                self.udp_socket.settimeout(1.0)  # Allow periodic checks of self.running
                data, addr = self.udp_socket.recvfrom(1024)
                question = data.decode('utf-8').strip()

                if question:
                    self.cli.log_question(question, "UDP")
                    logger.info(f"Received question from {addr}: {question}")

                    if question not in self.processed_questions:
                        self.processed_questions.add(question)
                        self.question_queue.put(question)
                    else:
                        self.cli.log_info(f"Duplicate question avoided: {question}")
                        logger.debug(f"Duplicate question ignored: {question}")

            except socket.timeout:
                continue  # Check if we should keep running
            except Exception as e:
                if self.running:  # Only log if we're supposed to be running
                    logger.error(f"Error in UDP listener: {e}")
                    console.print(f"[red]UDP listener error: {e}")
                break

    def _on_speech_recognized(self, speech_text: str):
        """
        Callback function called when speech is recognized.

        Args:
            speech_text: The recognized speech text
        """
        if speech_text and speech_text.strip():
            self.cli.log_question(speech_text, "Voice")
            logger.info(f"Speech recognized: {speech_text}")

            # Add to question queue for processing
            if speech_text not in self.processed_questions:
                self.processed_questions.add(speech_text)
                self.question_queue.put(speech_text)
            else:
                self.cli.log_info(f"Duplicate speech input avoided: {speech_text}")
                logger.debug(f"Duplicate speech input ignored: {speech_text}")

    def _on_speech_event(self, event: str):
        """Handle speech recognition events for CLI updates."""
        if event == 'recording_start':
            self.cli.log_speech_start()
        elif event == 'recording_stop':
            self.cli.log_speech_stop()

    def process_question(self):
        """Process questions from the queue."""
        logger.info("Started question processing thread")

        while self.running:
            try:
                # Use timeout to allow periodic checks of self.running
                question = self.question_queue.get(timeout=1.0)
                self.cli.update_status("Processing question...")
                logger.info(f"Processing question: {question}")

                # Get the response from AI
                self.cli.update_status("Generating AI response...")
                ai_response = self.ai_manager.chat_with_history(question)
                self.cli.log_response(ai_response)
                logger.info(f"AI response generated for question: {question}")

                # Save the interaction to history before generating TTS
                self.save_history(question, ai_response)

                # Synthesize and play the response
                self.cli.update_status("Synthesizing speech...")
                self.tts_manager.synthesize_and_play(
                    ai_response,
                    scene_name=self.config.obs_scene_name,
                    bot_source=self.config.obs_bot_source,
                    top_source=self.config.obs_top_source
                )

                self.cli.update_status("Ready")
                self.question_queue.task_done()

            except queue.Empty:
                continue  # Check if we should keep running
            except Exception as e:
                logger.error(f"Error processing question: {e}")
                self.cli.log_error(f"Error processing question: {e}")
                if not self.question_queue.empty():
                    self.question_queue.task_done()

    def load_history(self):
        """Load conversation history from file."""
        try:
            if os.path.exists(self.config.history_file):
                with open(self.config.history_file, "r", encoding='utf-8') as file:
                    history = json.load(file)
                    logger.info(f"Loaded {len(history)} conversation entries from history")
                    return history
        except Exception as e:
            logger.error(f"Error loading history: {e}")

        logger.info("Starting with empty conversation history")
        return []

    def save_history(self, question: str, response: str):
        """Save conversation to history file."""
        try:
            self.history.append({"question": question, "response": response})
            with open(self.config.history_file, "w", encoding='utf-8') as file:
                json.dump(self.history, file, indent=2, ensure_ascii=False)
            logger.debug(f"Saved conversation to history: {question[:50]}...")
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def start(self):
        """Start the voice assistant services."""
        self.running = True
        self.setup_udp_listener()

        # Start background threads
        udp_thread = threading.Thread(target=self.udp_listener, daemon=True)
        process_thread = threading.Thread(target=self.process_question, daemon=True)

        udp_thread.start()
        process_thread.start()

        # Start speech recognition if available
        try:
            if self.speech_manager.is_available():
                self.speech_manager.start_listening()
                self.cli.log_info(f"Speech recognition enabled! Press {self.config.push_to_talk_start_key}/{self.config.push_to_talk_stop_key}")
            else:
                self.cli.log_info("Speech recognition not available - continuing without microphone input")
        except Exception as e:
            logger.warning(f"Failed to start speech recognition: {e}")
            self.cli.log_error("Speech recognition failed to start")

        logger.info("CoHost.AI started successfully")
        self.cli.update_status("Ready")
        self.cli.start_display()

    def stop(self):
        """Stop the voice assistant services."""
        self.running = False
        self.cli.update_status("Shutting down...")

        # Stop speech recognition
        try:
            self.speech_manager.stop_listening()
            logger.info("Speech recognition stopped")
        except Exception as e:
            logger.error(f"Error stopping speech recognition: {e}")

        if self.udp_socket:
            try:
                self.udp_socket.close()
                logger.info("UDP socket closed")
            except Exception as e:
                logger.error(f"Error closing UDP socket: {e}")

        try:
            self.obs_manager.disconnect()
            logger.info("OBS connection closed")
        except Exception as e:
            logger.error(f"Error closing OBS connection: {e}")

        # Stop CLI display
        self.cli.stop_display()
        self.cli.show_shutdown_message()

        logger.info("CoHost.AI stopped")

    def run(self):
        """Run CoHost.AI with graceful shutdown."""
        try:
            # Show startup message
            self.cli.show_startup_message()

            self.start()

            # Keep running until interrupted
            while self.running:
                try:
                    time.sleep(1)
                except KeyboardInterrupt:
                    break

        except KeyboardInterrupt:
            pass  # Graceful shutdown
        finally:
            self.stop()
