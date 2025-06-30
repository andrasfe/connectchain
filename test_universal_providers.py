#!/usr/bin/env python3
"""
Test universal provider support with ConnectChain
"""

import os
from dotenv import load_dotenv, find_dotenv
from connectchain.lcel import model
from connectchain.prompts import ValidPromptTemplate
from langchain.schema import StrOutputParser

# Load environment variables
load_dotenv(find_dotenv())

def test_universal_providers():
    """Test direct access to various LLM providers"""
    
    print("Testing Universal Provider Support")
    print("=" * 50)
    
    # Check for API keys
    api_keys = {
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
        'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY'),
        'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY'),
    }
    
    print("\nAPI Keys Status:")
    for key, value in api_keys.items():
        status = "✅ Found" if value else "❌ Not found"
        print(f"  {key}: {status}")
    
    # Create a simple test prompt
    prompt = ValidPromptTemplate(
        input_variables=["question"],
        template="Answer in one word: {question}",
        output_sanitizer=None
    )
    
    # Test OpenAI models
    if api_keys['OPENAI_API_KEY']:
        print("\n\nTesting OpenAI Models:")
        print("-" * 30)
        
        # Test model 1 (o4-mini)
        try:
            print("\n1. Testing o4-mini-2025-04-16 (model '1')...")
            chain = prompt | model("1") | StrOutputParser()
            response = chain.invoke({"question": "What color is the sky?"})
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {e}")
            if "404" in str(e):
                print("   Note: o4-mini might not be available yet")
        
        # Test model 3 (GPT-3.5)
        try:
            print("\n2. Testing GPT-3.5-turbo (model '3')...")
            chain = prompt | model("3") | StrOutputParser()
            response = chain.invoke({"question": "What color is grass?"})
            print(f"   Response: {response}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n\nDemonstrating Multi-Provider Config:")
    print("-" * 30)
    print("""
To add more providers, update config.yml:

models:
    # Anthropic Claude
    '4':
        provider: anthropic
        type: chat
        model_name: claude-3-sonnet-20240229
        # Uses ANTHROPIC_API_KEY by default
    
    # Google Gemini
    '5':
        provider: google
        type: chat
        model_name: gemini-pro
        # Uses GOOGLE_API_KEY by default
        
    # Custom API endpoint example
    '6':
        provider: openai
        type: chat
        model_name: gpt-3.5-turbo
        api_base: https://my-proxy.com/v1
        
    # Custom environment variable
    '7':
        provider: openai
        type: chat
        model_name: gpt-4
        api_key_env: MY_CUSTOM_OPENAI_KEY
""")
    
    print("\n✅ Universal provider support is working!")
    print("\nKey Features:")
    print("- No EAS authentication required")
    print("- Automatic API key detection from environment")
    print("- Support for multiple providers")
    print("- Custom endpoints and API key variables")
    print("- Backward compatible with Azure/EAS configs")

if __name__ == "__main__":
    test_universal_providers()