#!/usr/bin/env python3
"""
Simple test script to verify OpenRouter connection works
Phase 1C: Piece 3.1
"""

import os
from openai import OpenAI

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Get configuration
API_KEY = os.getenv('OPENROUTER_API_KEY')
MODEL = os.getenv('GROK_MODEL', 'x-ai/grok-4')

print("=== OpenRouter Connection Test ===")
print(f"API Key: {API_KEY[:20]}..." if API_KEY else "API Key: NOT FOUND")
print(f"Model: {MODEL}")
print()

if not API_KEY:
    print("❌ ERROR: OPENROUTER_API_KEY not found in environment")
    print("Make sure .env file exists with OPENROUTER_API_KEY=...")
    exit(1)

# Initialize client
print("Initializing OpenRouter client...")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

# Test simple message
print(f"Testing connection with {MODEL}...")
try:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": "Hello! Respond with just 'OK' if you can hear me."}
        ],
        max_tokens=10
    )

    message_content = response.choices[0].message.content
    tokens_used = response.usage.total_tokens if response.usage else "Unknown"

    print()
    print("✅ SUCCESS!")
    print(f"Response: {message_content}")
    print(f"Tokens used: {tokens_used}")
    print()
    print("OpenRouter connection is working correctly!")

except Exception as e:
    print()
    print(f"❌ ERROR: {e}")
    print()
    print("Connection test failed. Check:")
    print("1. API key is valid")
    print("2. You have credits on OpenRouter")
    print("3. Model name is correct")
    exit(1)
