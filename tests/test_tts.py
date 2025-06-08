#!/usr/bin/env python3
"""
TTS Test Script for CoHost.AI.

This script provides independent testing of the text-to-speech functionality
to help debug audio issues and validate TTS configuration.

Author: Tom Pravetz
License: MIT

Usage:
    python test_tts.py

Requirements:
    - Google Cloud TTS credentials configured
    - Audio device properly configured
    - All dependencies installed
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to the path for imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / 'src'))

# Import with proper module path
from src.tts_manager import TTSManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_tts() -> bool:
    """
    Test TTS functionality independently.

    Performs a comprehensive test of the text-to-speech system including:
    - Google Cloud TTS client initialization
    - Audio device validation
    - Speech synthesis
    - Audio playback

    Returns:
        bool: True if all tests pass, False otherwise
    """
    # Configuration
    credentials_path = "cohost-442823-9d2a2fbbe9a4.json"
    test_device_index = 7  # Recommended device from audio test
    test_text = "Hello! This is a test of the text-to-speech system. Can you hear me?"

    # Validate prerequisites
    if not os.path.exists(credentials_path):
        print(f"❌ ERROR: Google Cloud credentials file not found: {credentials_path}")
        print("   Please ensure the file exists in the current directory.")
        return False

    tts_manager = None
    try:
        print("🔧 Initializing TTS Manager...")
        tts_manager = TTSManager(
            json_path=credentials_path,
            device_index=test_device_index,
            cache_enabled=False  # Disable cache for clean testing
        )
        print("✅ TTS Manager initialized successfully")

        print("🎵 Testing TTS synthesis and playback...")
        print(f"   Text: '{test_text}'")
        print(f"   Device: {test_device_index}")

        tts_manager.synthesize_and_play(test_text)

        print("✅ TTS test completed successfully!")
        print("   If you heard the audio, TTS is working correctly.")
        return True

    except Exception as e:
        print(f"❌ ERROR: TTS test failed: {e}")
        print("\n📋 Debug Information:")
        import traceback
        traceback.print_exc()
        return False

    finally:
        if tts_manager:
            try:
                tts_manager.cleanup()
                print("🧹 TTS Manager cleaned up")
            except Exception as cleanup_error:
                print(f"⚠️  Warning: Cleanup failed: {cleanup_error}")

if __name__ == "__main__":
    print("=" * 60)
    print("TTS TEST SCRIPT")
    print("=" * 60)
    
    success = test_tts()
    
    print("=" * 60)
    if success:
        print("✓ TTS test PASSED")
    else:
        print("✗ TTS test FAILED")
    print("=" * 60)
