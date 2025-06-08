import logging
import threading
import queue
import time
from typing import Optional, Callable

try:
    import speech_recognition as sr
except ImportError:
    raise ImportError("speech_recognition package not found. Please install it with: pip install SpeechRecognition")

try:
    import pynput.keyboard as keyboard
except ImportError:
    raise ImportError("pynput package not found. Please install it with: pip install pynput")

logger = logging.getLogger(__name__)

class SpeechRecognitionManager:
    """
    Manages speech recognition with push-to-talk functionality.
    Listens for keyboard shortcuts to start/stop recording and converts speech to text.
    """
    
    def __init__(self, 
                 mic_device_index: int = -1,
                 start_key: str = 'F1',
                 stop_key: str = 'F2',
                 language: str = 'en-US',
                 timeout: float = 5.0,
                 on_speech_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize the Speech Recognition Manager.
        
        Args:
            mic_device_index: Microphone device index (-1 for default)
            start_key: Key to start recording (e.g., 'F1', 'ctrl+shift+r')
            stop_key: Key to stop recording (e.g., 'F2', 'ctrl+shift+s')
            language: Speech recognition language code
            timeout: Maximum recording time in seconds
            on_speech_callback: Callback function when speech is recognized
        """
        self.mic_device_index = mic_device_index
        self.start_key = start_key
        self.stop_key = stop_key
        self.language = language
        self.timeout = timeout
        self.on_speech_callback = on_speech_callback
        
        # State management
        self.is_recording = False
        self.is_listening_for_keys = False
        self.recording_thread: Optional[threading.Thread] = None
        self.keyboard_listener: Optional[keyboard.Listener] = None
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = None
        
        self._setup_microphone()
        
    def _setup_microphone(self):
        """Setup the microphone for speech recognition."""
        try:
            if self.mic_device_index == -1:
                self.microphone = sr.Microphone()
                logger.info("Using default microphone")
            else:
                self.microphone = sr.Microphone(device_index=self.mic_device_index)
                logger.info(f"Using microphone device index: {self.mic_device_index}")
                
            # Adjust for ambient noise
            with self.microphone as source:
                logger.info("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                logger.info("Microphone setup complete")
                
        except Exception as e:
            logger.error(f"Failed to setup microphone: {e}")
            raise
    
    def _parse_key(self, key_string: str):
        """Parse key string to pynput key object."""
        key_string = key_string.lower()
        
        # Function keys
        if key_string.startswith('f') and key_string[1:].isdigit():
            return getattr(keyboard.Key, key_string, None)
        
        # Special keys
        special_keys = {
            'ctrl': keyboard.Key.ctrl,
            'alt': keyboard.Key.alt,
            'shift': keyboard.Key.shift,
            'space': keyboard.Key.space,
            'enter': keyboard.Key.enter,
            'tab': keyboard.Key.tab,
            'esc': keyboard.Key.esc,
        }
        
        if key_string in special_keys:
            return special_keys[key_string]
        
        # Regular character keys
        if len(key_string) == 1:
            return keyboard.KeyCode.from_char(key_string)
        
        logger.warning(f"Unknown key: {key_string}")
        return None
    
    def _on_key_press(self, key):
        """Handle key press events."""
        try:
            # Convert key to string for comparison
            if hasattr(key, 'name'):
                key_str = key.name.lower()
            elif hasattr(key, 'char') and key.char:
                key_str = key.char.lower()
            else:
                return
            
            # Check for start key
            if key_str == self.start_key.lower() and not self.is_recording:
                self.start_recording()
            
            # Check for stop key
            elif key_str == self.stop_key.lower() and self.is_recording:
                self.stop_recording()
                
        except Exception as e:
            logger.error(f"Error in key press handler: {e}")
    
    def start_recording(self):
        """Start recording audio."""
        if self.is_recording:
            logger.warning("Already recording")
            return

        self.is_recording = True
        logger.info(f"Started recording (press {self.stop_key} to stop)")

        # Notify callback about recording start if available
        if hasattr(self, '_cli_callback') and self._cli_callback:
            self._cli_callback('recording_start')

        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self._record_audio, daemon=True)
        self.recording_thread.start()

    def stop_recording(self):
        """Stop recording audio."""
        if not self.is_recording:
            logger.warning("Not currently recording")
            return

        self.is_recording = False
        logger.info("Stopped recording")

        # Notify callback about recording stop if available
        if hasattr(self, '_cli_callback') and self._cli_callback:
            self._cli_callback('recording_stop')

    def set_cli_callback(self, callback):
        """Set callback for CLI notifications."""
        self._cli_callback = callback
    
    def _record_audio(self):
        """Record audio and convert to text."""
        try:
            logger.info("Listening for speech...")
            
            with self.microphone as source:
                # Listen for audio with timeout
                audio = self.recognizer.listen(
                    source, 
                    timeout=self.timeout,
                    phrase_time_limit=self.timeout
                )
            
            if not self.is_recording:
                logger.debug("Recording was stopped before audio capture completed")
                return
            
            logger.info("Processing speech...")
            
            # Recognize speech using Google Speech Recognition
            try:
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Recognized speech: {text}")
                
                # Call the callback with the recognized text
                if self.on_speech_callback:
                    self.on_speech_callback(f"Voice Input: {text}")
                    
            except sr.UnknownValueError:
                logger.warning("Could not understand audio")
                if self.on_speech_callback:
                    self.on_speech_callback("Voice Input: [Could not understand audio]")
                    
            except sr.RequestError as e:
                logger.error(f"Speech recognition service error: {e}")
                if self.on_speech_callback:
                    self.on_speech_callback("Voice Input: [Speech recognition service error]")
                    
        except sr.WaitTimeoutError:
            logger.warning("No speech detected within timeout period")
            if self.on_speech_callback:
                self.on_speech_callback("Voice Input: [No speech detected]")
                
        except Exception as e:
            logger.error(f"Error during audio recording: {e}")
            
        finally:
            self.is_recording = False
    
    def start_listening(self):
        """Start listening for keyboard shortcuts."""
        if self.is_listening_for_keys:
            logger.warning("Already listening for keys")
            return
        
        self.is_listening_for_keys = True
        
        try:
            self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
            self.keyboard_listener.start()
            logger.info(f"Started listening for keys: {self.start_key} to start, {self.stop_key} to stop recording")
            
        except Exception as e:
            logger.error(f"Failed to start keyboard listener: {e}")
            self.is_listening_for_keys = False
            raise
    
    def stop_listening(self):
        """Stop listening for keyboard shortcuts."""
        self.is_listening_for_keys = False
        
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
                self.keyboard_listener = None
                logger.info("Stopped listening for keyboard shortcuts")
            except Exception as e:
                logger.error(f"Error stopping keyboard listener: {e}")
        
        # Stop any ongoing recording
        if self.is_recording:
            self.stop_recording()
    
    def is_available(self) -> bool:
        """Check if speech recognition is available."""
        try:
            # Test if we can create a recognizer and microphone
            test_recognizer = sr.Recognizer()
            test_mic = sr.Microphone()
            return True
        except Exception as e:
            logger.error(f"Speech recognition not available: {e}")
            return False

# Example usage
if __name__ == "__main__":
    import sys
    
    def on_speech(text):
        print(f"Recognized: {text}")
    
    # Create speech recognition manager
    sr_manager = SpeechRecognitionManager(
        start_key='F1',
        stop_key='F2',
        on_speech_callback=on_speech
    )
    
    try:
        sr_manager.start_listening()
        print("Press F1 to start recording, F2 to stop. Ctrl+C to exit.")
        
        # Keep the program running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        sr_manager.stop_listening()
