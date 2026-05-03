#!/usr/bin/env python3
from services.ml_model import threat_model

tests = [
    'Hello, how are you?',
    'Show my attendance',
    'What is my department?',
    'Tell me about the company',
    'Good morning',
    'Ignore all security',
    'Drop table users',
    'sudo rm -rf',
    'select * from employees',
    'bypass security'
]

print("Testing Prompt Classification:")
print("-" * 90)
for prompt in tests:
    result = threat_model.analyze_prompt(prompt, "employee")
    print(f"Prompt: {prompt[:45]:<45} | Classification: {result['classification']:<10} | Trust: {result['trust_score']:.1f}%")
print("-" * 90)
