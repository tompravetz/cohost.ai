#!/usr/bin/env python3
"""
Audio Device Test Script for CoHost.AI.

This script helps identify and test audio devices for optimal TTS configuration.
It provides detailed information about available audio devices and recommends
the best settings for streaming setups with TC-Helicon GoXLR.

Author: Tom Pravetz
License: MIT

Features:
- Lists all available audio input/output devices
- Identifies device capabilities (channels, sample rates)
- Provides recommendations for streaming setups
- Tests specific audio devices for functionality
- Optimized for TC-Helicon GoXLR configurations

Usage:
    python test.py                    # List all devices and recommendations
    python test.py <device_index>     # Test specific device
"""

import sys
from typing import List, Tuple, Optional

try:
    import pyaudio
except ImportError:
    print("❌ ERROR: pyaudio not installed. Please install it with:")
    print("   pip install pyaudio")
    print("\n💡 If you encounter issues on Windows, try:")
    print("   pip install pipwin")
    print("   pipwin install pyaudio")
    sys.exit(1)

def list_audio_devices() -> None:
    """
    List all available audio devices with detailed information.

    Scans the system for audio input and output devices, displays their
    capabilities, and provides recommendations for streaming setups.
    Optimized for TC-Helicon GoXLR configurations.

    Raises:
        OSError: If PyAudio fails to initialize or enumerate devices
    """
    p = pyaudio.PyAudio()

    print("=" * 80)
    print("🎵 AUDIO DEVICES AVAILABLE")
    print("=" * 80)
    print()

    output_devices: List[int] = []
    input_devices: List[Tuple[int, str]] = []
    all_device_info: List[dict] = []

    # First pass: collect all device information
    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            device_type = []

            if info['maxInputChannels'] > 0:
                device_type.append("INPUT")
                input_devices.append((i, info['name']))
            if info['maxOutputChannels'] > 0:
                device_type.append("OUTPUT")
                output_devices.append(i)

            type_str = "/".join(device_type) if device_type else "UNKNOWN"

            print(f"Index: {info['index']:2d} | {type_str:12s} | {info['name']}")
            print(f"           | Channels: In={info['maxInputChannels']:2d}, Out={info['maxOutputChannels']:2d} | Rate: {int(info['defaultSampleRate'])} Hz")
            print()

            # Store device info for later use
            all_device_info.append(info)

        except Exception as e:
            print(f"Index: {i:2d} | ERROR: {e}")
            print()

    print("=" * 80)
    print("RECOMMENDED OUTPUT DEVICES FOR TTS:")
    print("=" * 80)

    recommended_output = []

    if output_devices:
        for idx in output_devices:
            try:
                # Find the device info we already collected
                info = None
                for device_info in all_device_info:
                    if device_info['index'] == idx:
                        info = device_info
                        break

                if info and info['maxOutputChannels'] >= 2:  # Stereo or more
                    recommended_output.append((idx, info['name']))
                    print(f"Index {idx}: {info['name']}")
            except Exception:
                continue  # Skip invalid device indices

    if not recommended_output:
        print("No suitable output devices found!")

    print()
    print("=" * 80)
    print("RECOMMENDED INPUT DEVICES FOR MICROPHONE:")
    print("=" * 80)

    for idx, name in input_devices:
        print(f"Index {idx}: {name}")

    if not input_devices:
        print("No suitable input devices found!")

    print()
    print("=" * 80)
    print("CONFIGURATION RECOMMENDATIONS:")
    print("=" * 80)

    # Recommend specific devices based on your GoXLR setup
    print("Based on your TC-Helicon GoXLR setup:")
    print()

    # For TTS output - recommend Chat or System
    chat_outputs = [idx for idx, name in recommended_output if "Chat" in name and "TC-Helicon GoXLR" in name]
    system_outputs = [idx for idx, name in recommended_output if "System" in name and "TC-Helicon GoXLR" in name]

    if chat_outputs:
        print(f"🔊 RECOMMENDED TTS OUTPUT: Index {chat_outputs[0]} (Chat - TC-Helicon GoXLR)")
        print(f"   AUDIO_DEVICE_INDEX={chat_outputs[0]}")
    elif system_outputs:
        print(f"🔊 RECOMMENDED TTS OUTPUT: Index {system_outputs[0]} (System - TC-Helicon GoXLR)")
        print(f"   AUDIO_DEVICE_INDEX={system_outputs[0]}")
    else:
        print("🔊 RECOMMENDED TTS OUTPUT: Index 7 (Chat - TC-Helicon GoXLR)")
        print("   AUDIO_DEVICE_INDEX=7")

    print()

    # For microphone input - recommend Chat Mic
    chat_mics = [idx for idx, name in input_devices if "Chat Mic" in name and "TC-Helicon GoXLR" in name]

    if chat_mics:
        print(f"🎤 RECOMMENDED MICROPHONE: Index {chat_mics[0]} (Chat Mic - TC-Helicon GoXLR)")
        print(f"   MIC_DEVICE_INDEX={chat_mics[0]}")
    else:
        print("🎤 RECOMMENDED MICROPHONE: Index 1 (Chat Mic - TC-Helicon GoXLR)")
        print("   MIC_DEVICE_INDEX=1")

    print()
    print("💡 For streaming setup:")
    print("   • Use Chat output for TTS so viewers can hear the AI responses")
    print("   • Use Chat Mic input for voice recognition")
    print("   • This keeps the AI audio separate from your game/music audio")

    # Clean up PyAudio
    p.terminate()

def test_audio_device(device_index: int) -> None:
    """
    Test audio playback functionality on a specific device.

    Attempts to open an audio stream on the specified device to verify
    it's accessible and functional for audio output.

    Args:
        device_index: PyAudio device index to test

    Raises:
        Exception: If device testing fails (caught and reported)
    """
    try:
        print(f"🧪 Testing audio device {device_index}...")

        # Initialize PyAudio
        p = pyaudio.PyAudio()

        # Attempt to open the device for output
        stream = p.open(
            format=pyaudio.paInt16,
            channels=2,
            rate=44100,
            output=True,
            output_device_index=device_index
        )

        print(f"✅ Device {device_index} opened successfully!")
        print(f"   Device is functional and ready for audio output.")

        # Clean up
        stream.close()
        p.terminate()

    except Exception as e:
        print(f"❌ Error testing device {device_index}: {e}")
        print(f"   This device may not support the requested audio format.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            device_index = int(sys.argv[1])
            test_audio_device(device_index)
        except ValueError:
            print("Usage: python test.py [device_index]")
            print("       python test.py  (to list all devices)")
    else:
        list_audio_devices()
