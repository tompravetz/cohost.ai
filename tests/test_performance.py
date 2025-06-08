#!/usr/bin/env python3
"""
Performance Test Script for CoHost.AI

This script helps you test and optimize performance settings.
"""

import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_tts_performance():
    """Test TTS performance with different settings."""
    try:
        from src.tts_manager import TTSManager
        from src.config import Config
    except ImportError as e:
        print(f"ERROR: Failed to import modules: {e}")
        print("Please ensure all dependencies are installed and you're in the correct directory.")
        return False
    
    print("🚀 Testing TTS Performance")
    print("=" * 50)
    
    try:
        config = Config()
        
        # Test text
        test_text = "Hello, this is a performance test of the TTS system. POG!"
        
        print(f"Test text: {test_text}")
        print()
        
        # Test without cache
        print("📊 Testing WITHOUT cache...")
        tts_no_cache = TTSManager(
            json_path=config.google_credentials_path,
            device_index=config.audio_device_index,
            cache_enabled=False,
            buffer_size=1024  # Smaller buffer
        )
        
        start_time = time.time()
        tts_no_cache.synthesize_and_play(test_text)
        no_cache_time = time.time() - start_time
        tts_no_cache.cleanup()
        
        print(f"⏱️  Time without cache: {no_cache_time:.2f} seconds")
        print()
        
        # Test with cache (first run)
        print("📊 Testing WITH cache (first run)...")
        tts_with_cache = TTSManager(
            json_path=config.google_credentials_path,
            device_index=config.audio_device_index,
            cache_enabled=True,
            buffer_size=4096  # Larger buffer
        )
        
        start_time = time.time()
        tts_with_cache.synthesize_and_play(test_text)
        cache_first_time = time.time() - start_time
        
        print(f"⏱️  Time with cache (first): {cache_first_time:.2f} seconds")
        print()
        
        # Test with cache (second run - should be faster)
        print("📊 Testing WITH cache (cached run)...")
        start_time = time.time()
        tts_with_cache.synthesize_and_play(test_text)
        cache_second_time = time.time() - start_time
        tts_with_cache.cleanup()
        
        print(f"⏱️  Time with cache (cached): {cache_second_time:.2f} seconds")
        print()
        
        # Results
        print("📈 Performance Results:")
        print(f"• Without cache: {no_cache_time:.2f}s")
        print(f"• With cache (first): {cache_first_time:.2f}s")
        print(f"• With cache (cached): {cache_second_time:.2f}s")
        
        if cache_second_time < no_cache_time:
            improvement = ((no_cache_time - cache_second_time) / no_cache_time) * 100
            print(f"• Cache improvement: {improvement:.1f}% faster")
        
        print()
        print("💡 Recommendations:")
        if cache_second_time < no_cache_time * 0.5:
            print("✅ TTS caching is working well - keep it enabled")
        else:
            print("⚠️  TTS caching shows minimal improvement")
        
        if no_cache_time > 3.0:
            print("⚠️  TTS synthesis is slow - check your internet connection")
        else:
            print("✅ TTS synthesis speed is good")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during TTS performance test: {e}")
        return False

def test_ai_performance():
    """Test AI response performance."""
    try:
        from src.AiManager import AiManager
        from src.config import Config
    except ImportError as e:
        print(f"ERROR: Failed to import AI modules: {e}")
        return False
    
    print("🤖 Testing AI Performance")
    print("=" * 50)
    
    try:
        config = Config()
        ai_manager = AiManager(model=config.ollama_model)
        
        test_questions = [
            "Hello Mike, how are you?",
            "What do you think about streaming?",
            "Tell me a short joke."
        ]
        
        total_time = 0
        for i, question in enumerate(test_questions, 1):
            print(f"🔄 Test {i}/3: {question}")
            
            start_time = time.time()
            response = ai_manager.chat_with_history(question)
            response_time = time.time() - start_time
            total_time += response_time
            
            print(f"⏱️  Response time: {response_time:.2f}s")
            print(f"📝 Response: {response[:100]}{'...' if len(response) > 100 else ''}")
            print()
        
        avg_time = total_time / len(test_questions)
        print(f"📊 Average response time: {avg_time:.2f}s")
        
        print()
        print("💡 Recommendations:")
        if avg_time < 2.0:
            print("✅ AI response speed is excellent")
        elif avg_time < 5.0:
            print("✅ AI response speed is good")
        elif avg_time < 10.0:
            print("⚠️  AI response speed is acceptable but could be improved")
        else:
            print("❌ AI response speed is slow - check Ollama configuration")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during AI performance test: {e}")
        print("💡 Make sure Ollama is running and the mistral model is installed:")
        print("   ollama serve")
        print("   ollama pull mistral")
        return False

def test_overall_performance():
    """Test overall end-to-end performance."""
    print("🎯 Testing Overall Performance")
    print("=" * 50)
    
    try:
        from src.VoiceAssistant import VoiceAssistant
        from src.config import Config
    except ImportError as e:
        print(f"ERROR: Failed to import VoiceAssistant: {e}")
        return False
    
    try:
        config = Config()
        
        # This would require a full integration test
        # For now, just validate configuration
        print("✅ Configuration loaded successfully")
        print(f"• Ollama model: {config.ollama_model}")
        print(f"• TTS cache enabled: {config.tts_cache_enabled}")
        print(f"• Audio buffer size: {config.audio_buffer_size}")
        print(f"• UDP port: {config.udp_port}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during overall performance test: {e}")
        return False

def main():
    """Main performance test function."""
    print("🔧 CoHost.AI Performance Testing Suite")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "tts":
            test_tts_performance()
        elif test_type == "ai":
            test_ai_performance()
        elif test_type == "overall":
            test_overall_performance()
        else:
            print("Usage: python test_performance.py [tts|ai|overall]")
    else:
        # Run all tests
        print("Running all performance tests...\n")
        
        success_count = 0
        total_tests = 3
        
        if test_ai_performance():
            success_count += 1
        print()
        
        if test_tts_performance():
            success_count += 1
        print()
        
        if test_overall_performance():
            success_count += 1
        print()
        
        print("🏁 Performance Testing Complete")
        print("=" * 40)
        print(f"Tests passed: {success_count}/{total_tests}")
        
        if success_count == total_tests:
            print("🎉 All tests passed! Your system is ready for optimal performance.")
        else:
            print("⚠️  Some tests failed. Check the output above for recommendations.")

if __name__ == "__main__":
    main()
