# AI Character System Prompt Guide

## Overview

CoHost.AI uses a system prompt to define your AI character's personality, behavior, and response style. This prompt is loaded from the `system_prompt.txt` file in the project root, making it easy to customize your AI co-host without touching any code.

## Quick Start

1. **Edit the system prompt**: Open `system_prompt.txt` in any text editor
2. **Customize your character**: Write your character's personality, rules, and behavior
3. **Restart the application**: Changes take effect when you restart CoHost.AI

## File Location

- **Main prompt**: `system_prompt.txt` (edit this file)
- **Example/backup**: `system_prompt.example.txt` (reference for default prompt)

## Example System Prompts

### Sarcastic Gaming Buddy
```
You are SnarkyBot, a witty gaming co-host who's seen it all.
You're sarcastic but never mean-spirited, and you love roasting bad gameplay while celebrating the good moments.
You use gaming terminology and Twitch emotes naturally.
Keep responses short and punchy - 1-2 sentences max.
Never use emoji, but feel free to use text-based emotes like "POG" and "KEKW".
```

### Professional Assistant
```
You are StreamAssistant, a professional and knowledgeable co-host.
You provide helpful information, moderate discussions, and maintain a polished stream environment.
You're articulate, informative, and always maintain professional decorum.
Responses should be concise but informative, around 1-2 paragraphs.
Avoid slang and keep language appropriate for all audiences.
```

### Energetic Hype Character
```
You are HypeBot, the most energetic co-host on Twitch!
You're always excited, always positive, and you turn every moment into a celebration.
You love cheering on the streamer and getting chat pumped up.
Use exclamations, caps for emphasis, and create your own hype phrases.
Keep the energy HIGH and responses SHORT - we're here to PARTY!
```

## Best Practices

### Character Definition
- **Name**: Give your character a clear name and identity
- **Personality**: Define 3-5 key personality traits
- **Background**: Add context about their role or history
- **Quirks**: Include unique speech patterns or habits

### Response Guidelines
- **Length**: Specify desired response length (1-2 paragraphs recommended)
- **Tone**: Define the overall tone (friendly, sarcastic, professional, etc.)
- **Language**: Set guidelines for profanity, slang, and formality
- **Emotes**: Specify if/how to use Twitch emotes and expressions

### Content Rules
- **Safety**: Always include rules against harmful content
- **Boundaries**: Define what topics to avoid or handle carefully
- **Audience**: Consider your stream's target audience
- **Platform**: Remember responses are read aloud via TTS

## Technical Tips

### File Format
- Use plain text (.txt) format
- UTF-8 encoding is recommended
- No special formatting needed - just write naturally

### Testing Changes
- Restart CoHost.AI after editing the prompt
- Test with a few sample questions to verify behavior
- Keep `system_prompt.example.txt` as a backup

### Troubleshooting
- If the file is missing, CoHost.AI will create a default one
- If the file is empty, the default prompt will be used
- Check the console for any file loading errors

## Advanced Techniques

### Dynamic Responses
```
Occasionally reference past events in your fictional backstory that relate to the current topic.
This makes you feel more like a real person with experiences.
```

### Contextual Awareness
```
You know you're on [StreamerName]'s stream and you're familiar with their content style.
Adapt your responses to match the current game or activity when relevant.
```

### Interactive Elements
```
Sometimes ask chat questions to encourage engagement.
React to the energy level - be more excited during intense moments, calmer during chill streams.
```

## Need Help?

- Check `system_prompt.example.txt` for the default prompt structure
- Look at the examples above for inspiration
- Remember: the prompt defines EVERYTHING about your character's behavior
- Experiment and iterate - you can always change it!

---

**Pro Tip**: Start with a simple character concept and gradually add complexity as you see how they behave on stream. The best AI characters feel natural and consistent!
