#!/usr/bin/env python3
"""
Speech Recognition Test Script for CoHost.AI

This script helps you test speech recognition functionality.
"""

import sys
import time

def test_speech_recognition():
    """Test speech recognition functionality."""
    try:
        from src.SpeechRecognitionManager import SpeechRecognitionManager
    except ImportError as e:
        print(f"ERROR: Failed to import SpeechRecognitionManager: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install SpeechRecognition pynput")
        return False
    
    def on_speech_callback(text):
        print(f"✅ Recognized: {text}")
    
    print("🎤 Testing Speech Recognition")
    print("=" * 50)
    
    try:
        # Create speech recognition manager
        sr_manager = SpeechRecognitionManager(
            mic_device_index=-1,  # Use default microphone
            start_key='F1',
            stop_key='F2',
            language='en-US',
            timeout=10.0,
            on_speech_callback=on_speech_callback
        )
        
        if not sr_manager.is_available():
            print("❌ Speech recognition is not available")
            return False
        
        print("✅ Speech recognition is available")
        print()
        print("Starting speech recognition test...")
        print("Press F1 to start recording, F2 to stop recording")
        print("Press Ctrl+C to exit")
        print()
        
        sr_manager.start_listening()
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Test interrupted by user")
        
        sr_manager.stop_listening()
        print("✅ Speech recognition test completed")
        return True
        
    except Exception as e:
        print(f"❌ Error during speech recognition test: {e}")
        return False

def test_microphone_devices():
    """List available microphone devices."""
    try:
        import speech_recognition as sr
    except ImportError:
        print("ERROR: speech_recognition not installed. Please install it with:")
        print("pip install SpeechRecognition")
        return
    
    print("🎤 Available Microphone Devices")
    print("=" * 50)
    
    try:
        mic_list = sr.Microphone.list_microphone_names()
        
        if not mic_list:
            print("No microphone devices found")
            return
        
        for i, name in enumerate(mic_list):
            print(f"Index {i}: {name}")
        
        print()
        print("To use a specific microphone, set MIC_DEVICE_INDEX in your .env file")
        print("Example: MIC_DEVICE_INDEX=1")
        print("Use -1 for the default microphone")
        
    except Exception as e:
        print(f"Error listing microphone devices: {e}")

def main():
    """Main test function."""
    if len(sys.argv) > 1 and sys.argv[1] == "devices":
        test_microphone_devices()
    else:
        print("CoHost.AI Speech Recognition Test")
        print("=" * 40)
        print()
        
        # Test microphone devices first
        test_microphone_devices()
        print()
        
        # Test speech recognition
        if test_speech_recognition():
            print("🎉 Speech recognition test completed successfully!")
        else:
            print("❌ Speech recognition test failed")
            print()
            print("Troubleshooting tips:")
            print("1. Check microphone permissions")
            print("2. Ensure you have an internet connection")
            print("3. Try running: python test_speech.py devices")
            print("4. Check your .env file configuration")

if __name__ == "__main__":
    main()
