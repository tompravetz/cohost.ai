# 🤖 CoHost.AI - AI-Powered Streaming Co-Host

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A sophisticated, production-ready AI streaming companion that provides real-time interaction through voice recognition, AI responses, and text-to-speech synthesis. Built with modern Python practices, comprehensive error handling, and optimized for professional streaming environments.

## 🌟 Key Features

### 🎯 Core Functionality
- **🔊 Advanced Text-to-Speech**: Google Cloud TTS with intelligent caching and direct memory playback
- **🎤 Speech Recognition**: Push-to-talk voice input with configurable hotkeys
- **🤖 AI Response Generation**: Local AI inference using Ollama with character personality
- **📡 Real-time Chat Integration**: UDP broadcast listening for Streamer.bot integration
- **📺 OBS Studio Integration**: Automatic character visibility and scene management

### ⚡ Performance & Reliability
- **🚀 Optimized Audio Pipeline**: Direct memory audio playback (no temporary files)
- **💾 Intelligent Caching**: TTS response caching for improved performance
- **🔄 Parallel Processing**: Multi-threaded architecture for responsive operation
- **🛡️ Robust Error Handling**: Comprehensive exception handling and graceful degradation
- **📊 Real-time Monitoring**: Beautiful CLI interface with live status updates

### 🔧 Developer-Friendly
- **📝 Comprehensive Documentation**: Detailed docstrings and type hints throughout
- **🧪 Testing Suite**: Independent test scripts for all major components
- **⚙️ Flexible Configuration**: Environment-based configuration with validation
- **📋 Professional Logging**: Structured logging with multiple output formats

## Character: Mike Oxlong

Mike is a sarcastic, misanthropic Canadian character who reluctantly appears on TompTTV's Twitch stream. He's known for:
- Overly sarcastic and snarky responses
- Extreme sassiness and misanthropy
- Confidence that he's not an AI (but suspicious everyone else might be)
- Using Twitch emotes like "POG" in daily speech
- Creating custom exclamations with profanity
- Short, punchy responses (1-2 paragraphs)

## Prerequisites

1. **Python 3.8+**
2. **OBS Studio** with WebSocket plugin enabled
3. **Ollama** installed and running with Mistral model
4. **Google Cloud TTS** service account credentials
5. **Streamer.bot** configured to send UDP broadcasts

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd "CoHost.AI"
   ```

   **Note**: If your directory is named "Mike 2.0" (with a space), you may encounter issues with the setup script. Run `migrate_directory.bat` on Windows to rename it to "CoHost.AI", or manually rename the directory.

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # or
   source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Ollama**:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull mistral
   ```

5. **Setup Google Cloud Credentials**:
   ```bash
   # Copy the credentials template
   cp credentials.example.json your-credentials.json
   # Edit your-credentials.json with your actual Google Cloud service account details
   ```

6. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your actual values (especially GOOGLE_CREDENTIALS_PATH)
   ```

## Configuration

Create a `.env` file with the following variables:

```env
# Google Cloud Text-to-Speech
GOOGLE_CREDENTIALS_PATH=path/to/your/google-credentials.json

# UDP Configuration
UDP_PORT=5005

# OBS WebSocket Configuration
OBS_HOST=localhost
OBS_PORT=4455
OBS_PASSWORD=your_obs_websocket_password

# Audio Configuration
AUDIO_DEVICE_INDEX=7

# OBS Scene and Source Names
OBS_SCENE_NAME=In-Game [OLD]
OBS_BOT_SOURCE=AIBot
OBS_TOP_SOURCE=AITop

# Ollama Configuration
OLLAMA_MODEL=mistral

# Logging Level
LOG_LEVEL=INFO

# Microphone Configuration
MIC_DEVICE_INDEX=-1
PUSH_TO_TALK_START_KEY=F1
PUSH_TO_TALK_STOP_KEY=F2
SPEECH_RECOGNITION_LANGUAGE=en-US
SPEECH_RECOGNITION_TIMEOUT=5.0

# Performance Configuration
ENABLE_PARALLEL_PROCESSING=true
TTS_CACHE_ENABLED=true
TTS_CACHE_SIZE=50
AUDIO_BUFFER_SIZE=4096

# UI Configuration
SHOW_DETAILED_LOGS=false
CLI_REFRESH_RATE=0.1
```

## Usage

1. **Start Ollama** (if not running as service):
   ```bash
   ollama serve
   ```

2. **Start OBS Studio** with WebSocket server enabled

3. **Run the Voice Assistant**:
   ```bash
   python run.py
   ```

4. **Configure Streamer.bot** to send UDP broadcasts to `localhost:5005`

5. **Test your setup** (optional):
   ```bash
   python test.py              # Test audio devices
   python test_speech.py       # Test speech recognition
   python test_performance.py  # Test performance
   ```

## Voice Input Usage

Once running, you can interact with Mike in two ways:

1. **Chat Integration**: Messages from Twitch chat via Streamer.bot
2. **Voice Input**: Use keyboard shortcuts for push-to-talk
   - Press **F1** (or your configured key) to start recording
   - Speak your message
   - Press **F2** (or your configured key) to stop recording
   - Your speech will be converted to text and sent to Mike for response

## Project Structure

```
CoHost.AI/
├── src/                              # Main source code package
│   ├── __init__.py                  # Package initialization
│   ├── VoiceAssistant.py            # Main application orchestrator
│   ├── AiManager.py                 # AI response generation (Ollama)
│   ├── OBSWebsocketsManager.py      # OBS Studio integration
│   ├── tts_manager.py               # Text-to-speech management
│   ├── SpeechRecognitionManager.py  # Speech recognition and push-to-talk
│   ├── cli_interface.py             # Command-line interface
│   └── config.py                    # Configuration management
├── tests/                           # Test suite
│   ├── __init__.py                  # Test package initialization
│   ├── test.py                      # Audio device testing
│   ├── test_tts.py                  # TTS functionality testing
│   ├── test_speech.py               # Speech recognition testing
│   └── test_performance.py          # Performance benchmarking
├── run.py                           # Application entry point
├── setup.py                         # Package installation configuration
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment configuration template
├── credentials.example.json         # Google Cloud credentials template
├── .gitignore                       # Git ignore rules
├── LICENSE                          # MIT License
├── CONTRIBUTING.md                  # Contribution guidelines
├── PORTFOLIO_IMPROVEMENTS.md        # Development improvements summary
└── README.md                        # This documentation
```

## Troubleshooting

### Common Issues

1. **Setup fails with "is not recognized as internal or external command"**
   - This happens when the directory name contains spaces (e.g., "Mike 2.0")
   - **Solution 1**: Run `migrate_directory.bat` to rename to "CoHost.AI"
   - **Solution 2**: Manually rename the directory to remove spaces
   - **Solution 3**: Use the updated `setup.py` which handles spaces better

2. **"Could not connect to OBS"**
   - Ensure OBS is running
   - Check WebSocket server is enabled in OBS
   - Verify connection details in `.env`

3. **"Ollama connection failed"**
   - Ensure Ollama is running: `ollama serve`
   - Check if Mistral model is installed: `ollama list`

4. **"Google credentials not found"**
   - Verify the path in `GOOGLE_CREDENTIALS_PATH`
   - Ensure the service account has TTS permissions

5. **Audio playback issues**
   - Run `python test.py` to list audio devices
   - Update `AUDIO_DEVICE_INDEX` in `.env`

6. **Speech recognition not working**
   - Check microphone permissions
   - Run `python test.py` to find your microphone device index
   - Update `MIC_DEVICE_INDEX` in `.env`
   - Ensure you have an internet connection (uses Google Speech Recognition)

### Logs

Check `voice_assistant.log` for detailed error information.

## Development

### Adding New Features

1. Follow the existing code structure
2. Add proper error handling and logging
3. Update configuration in `config.py` if needed
4. Add tests for new functionality

### Code Style

- Use type hints
- Follow PEP 8
- Add docstrings to all functions
- Use logging instead of print statements

## 🏗️ Architecture

### System Design
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamer.bot  │───▶│   CoHost.AI     │───▶│   OBS Studio    │
│   (UDP Sender)  │    │  (Main System)  │    │  (Scene Mgmt)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Google Cloud   │
                    │      TTS        │
                    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   Audio Output  │
                    │  (TC-Helicon)   │
                    └─────────────────┘
```

### Component Overview
- **VoiceAssistant**: Main orchestrator and UDP listener
- **AiManager**: Ollama integration for character responses
- **TTSManager**: Google Cloud TTS with caching and audio optimization
- **SpeechRecognitionManager**: Push-to-talk voice input handling
- **OBSWebsocketsManager**: OBS Studio integration for visual effects
- **CLIInterface**: Real-time status dashboard and user interface

## 🧪 Testing

### Available Test Scripts
```bash
# Test audio device configuration
python test.py

# Test specific audio device
python test.py 7

# Test TTS functionality
python test_tts.py

# Test speech recognition
python test_speech.py

# Performance benchmarking
python test_performance.py
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html
```

## 📈 Performance Metrics

- **TTS Response Time**: ~2-3 seconds (with caching: ~0.1 seconds)
- **Speech Recognition**: ~1-2 seconds processing time
- **Memory Usage**: ~50-100MB typical operation
- **Audio Latency**: <100ms for cached responses

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Start for Contributors
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes with proper documentation
4. Add tests for new functionality
5. Ensure all tests pass: `python -m pytest`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Cloud TTS** for high-quality speech synthesis
- **Ollama** for local AI inference capabilities
- **OBS Studio** for streaming integration
- **Rich** for beautiful terminal interfaces
- **PyAudio** for cross-platform audio handling

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/tompravetz/cohost.ai/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tompravetz/cohost.ai/discussions)
- **Documentation**: [Project Wiki](https://github.com/tompravetz/cohost.ai/wiki)

---

**Built with ❤️ by [Tom Pravetz](https://github.com/tompravetz)**

*CoHost.AI - Bringing AI personalities to life in streaming environments*
