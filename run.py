#!/usr/bin/env python3
"""
CoHost.AI Application Entry Point.

This script serves as the main entry point for the CoHost.AI streaming
co-host application. It handles initialization, configuration loading,
and graceful shutdown.

Author: Tom Pravetz
License: MIT

Usage:
    python run.py

Environment Variables:
    See .env.example for required configuration variables.
"""

import sys
import logging

from dotenv import load_dotenv

from src.config import Config, setup_logging
from src.VoiceAssistant import VoiceAssistant

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main entry point for the CoHost.AI application.

    Initializes logging, loads configuration, and starts the voice assistant.
    Handles graceful shutdown on keyboard interrupt and logs fatal errors.

    Raises:
        SystemExit: On fatal errors or configuration issues
    """
    try:
        # Setup logging configuration first
        setup_logging()
        logger.info("Starting CoHost.AI application")

        # Load and validate configuration
        config = Config()
        logger.info(f"Configuration loaded: {config}")

        # Initialize and run the voice assistant
        assistant = VoiceAssistant(config)
        assistant.run()

    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down gracefully")
        print("\n🛑 Shutting down gracefully...")

    except Exception as e:
        logger.critical(f"Fatal error during startup: {e}", exc_info=True)
        print(f"❌ Fatal error: {e}")
        print("Check the logs for more details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
