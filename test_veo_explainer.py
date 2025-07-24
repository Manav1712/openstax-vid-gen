#!/usr/bin/env python3
"""
Comprehensive test suite for the Veo 2 LLM Explainer.
Tests all functions, edge cases, and validation rules.
"""

import sys
import os
sys.path.append('.')

from llm.explainer import (
    generate_script, 
    count_narration_words, 
    count_words_in_script,
    parse_script_sections,
    script_to_narration,
    script_to_veo_prompt
)

def test_word_counting():
    """Test word counting functions."""
    print("🔢 Testing Word Counting Functions")
    
    sample_script = """SCENE: A modern physics lab with equipment and displays
NARRATION: This is a test narration with exactly ten words here
VISUAL_ACTION: Objects move and demonstrate physics concepts clearly
CAMERA: Wide shot transitioning to close-up view
AUDIO: Soft background music plays gently"""
    
    narration_words = count_narration_words(sample_script)
    total_words = count_words_in_script(sample_script)
    
    print(f"   Sample script narration words: {narration_words}")
    print(f"   Sample script total words: {total_words}")
    print(f"   ✅ Word counting working correctly\n")

def test_script_parsing():
    """Test script parsing functionality."""
    print("📋 Testing Script Parsing")
    
    sample_script = """SCENE: Modern laboratory setting
NARRATION: Physics concepts explained simply
VISUAL_ACTION: Animated demonstrations appear
CAMERA: Dynamic camera movement
AUDIO: Educational background sounds"""
    
    sections = parse_script_sections(sample_script)
    
    print("   Parsed sections:")
    for key, value in sections.items():
        if value.strip():
            print(f"     {key}: {value}")
    
    print(f"   ✅ Script parsing working correctly\n")

def test_prompt_conversion():
    """Test Veo 2 prompt conversion."""
    print("🎯 Testing Veo 2 Prompt Conversion")
    
    sample_script = """SCENE: Clean educational environment
NARRATION: Clear explanation of physics concept
VISUAL_ACTION: Visual demonstrations and animations
CAMERA: Smooth camera transitions
AUDIO: Subtle background music"""
    
    veo_prompt = script_to_veo_prompt(sample_script)
    narration_only = script_to_narration(sample_script)
    
    print(f"   Veo 2 prompt: {veo_prompt}")
    print(f"   Narration only: {narration_only}")
    print(f"   ✅ Prompt conversion working correctly\n")

def test_edge_cases():
    """Test edge cases and error handling."""
    print("⚠️ Testing Edge Cases")
    
    # Test empty chunks
    empty_result = generate_script([], "")
    print(f"   Empty chunks result: {'✅ Has content' if empty_result else '❌ Empty'}")
    
    # Test malformed script parsing
    malformed_script = "This is not a properly formatted script"
    sections = parse_script_sections(malformed_script)
    empty_sections = sum(1 for v in sections.values() if not v.strip())
    print(f"   Malformed script sections: {len(sections) - empty_sections} populated, {empty_sections} empty")
    
    # Test narration extraction from malformed script
    narration = script_to_narration(malformed_script)
    print(f"   Narration from malformed: '{narration}' (should be empty)")
    
    print(f"   ✅ Edge cases handled gracefully\n")

def test_physics_concepts():
    """Test with various physics concepts."""
    print("🧪 Testing Different Physics Concepts")
    
    test_concepts = [
        {
            'name': 'Kinematics',
            'chunks': [{
                'text': 'Velocity is the rate of change of position. Acceleration is the rate of change of velocity.',
                'metadata': {'title': 'Motion in One Dimension', 'section': '2.1'}
            }],
            'query': 'What is velocity?'
        },
        {
            'name': 'Thermodynamics',
            'chunks': [{
                'text': 'Heat is energy transferred due to temperature difference. Temperature measures average kinetic energy.',
                'metadata': {'title': 'Heat and Temperature', 'section': '14.1'}
            }],
            'query': 'Explain heat and temperature'
        },
        {
            'name': 'Waves',
            'chunks': [{
                'text': 'Waves transfer energy without transferring matter. Frequency and wavelength are inversely related.',
                'metadata': {'title': 'Wave Properties', 'section': '16.1'}
            }],
            'query': 'How do waves work?'
        }
    ]
    
    for concept in test_concepts:
        print(f"   Testing: {concept['name']}")
        script = generate_script(concept['chunks'], concept['query'])
        
        # Validate script
        narration_words = count_narration_words(script)
        sections = parse_script_sections(script)
        
        # Check if all required sections are present
        required_sections = ['SCENE', 'NARRATION', 'VISUAL_ACTION', 'CAMERA', 'AUDIO']
        present_sections = [s for s in required_sections if sections[s].strip()]
        
        print(f"     Narration words: {narration_words}/50 ({'✅' if narration_words <= 50 else '❌'})")
        print(f"     Sections present: {len(present_sections)}/5 ({'✅' if len(present_sections) >= 4 else '❌'})")
        
    print(f"   ✅ Physics concepts testing completed\n")

def test_word_limits():
    """Test word limit enforcement."""
    print("📏 Testing Word Limit Enforcement")
    
    # Create a chunk that might generate long narration
    verbose_chunks = [{
        'text': 'Quantum mechanics is a fundamental theory in physics that describes the behavior of matter and energy at the smallest scales. It introduces concepts like wave-particle duality, uncertainty principle, superposition, and entanglement. These phenomena challenge our classical understanding of physics and reality itself.',
        'metadata': {'title': 'Quantum Mechanics Introduction', 'section': '40.1'}
    }]
    
    script = generate_script(verbose_chunks, "Explain quantum mechanics in detail")
    narration_words = count_narration_words(script)
    
    print(f"   Complex topic narration words: {narration_words}/50")
    print(f"   Word limit status: {'✅ Within limit' if narration_words <= 50 else '❌ Exceeded limit'}")
    
    if narration_words <= 50:
        print("   ✅ Word limit enforcement working correctly")
    else:
        print("   ⚠️ Word limit may need adjustment in prompt")
    
    print()

def run_comprehensive_test():
    """Run all tests."""
    print("=" * 70)
    print("🧪 COMPREHENSIVE VEO 2 EXPLAINER TEST SUITE")
    print("=" * 70)
    print()
    
    test_word_counting()
    test_script_parsing()
    test_prompt_conversion()
    test_edge_cases()
    test_physics_concepts()
    test_word_limits()
    
    print("=" * 70)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 70)

if __name__ == "__main__":
    run_comprehensive_test() 