#!/usr/bin/env python3
"""
Test script để kiểm tra npr_get_text_and_mp3.py
"""

import sys
import os

# Test với URL mẫu
test_url = "https://www.npr.org/transcripts/nx-s1-5655252"

# Simulate user input
class MockInput:
    def __init__(self, return_value):
        self.return_value = return_value
        self.call_count = 0
    
    def __call__(self, prompt):
        self.call_count += 1
        print(f"{prompt}{self.return_value}")
        return self.return_value

# Import và test
if __name__ == "__main__":
    # Thay thế input function
    original_input = __builtins__.input
    __builtins__.input = MockInput(test_url)
    
    # Import script
    try:
        import npr_get_text_and_mp3
        print("\n✅ Script imported successfully!")
        
        # Run main
        print("\n" + "="*70)
        print("TESTING SCRIPT...")
        print("="*70 + "\n")
        
        npr_get_text_and_mp3.main()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Restore original input
        __builtins__.input = original_input
