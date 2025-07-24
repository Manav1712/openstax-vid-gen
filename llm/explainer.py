import os
import openai
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_script(chunks: List[Dict], user_query: str = "") -> str:
    """
    Generate a 8 -second Veo 2 educational video script from retrieved chunks.
    
    Args:
        chunks: List of chunk dictionaries with 'text' and 'metadata'
        user_query: Original user question (optional, for context)
        
    Returns:
        String containing the Veo 2 scene description script
    """
    
    # Combine chunk texts with context delimiters
    combined_text = "\n\n".join([chunk['text'] for chunk in chunks])
    
    # Get primary section title for focus
    primary_section = chunks[0]['metadata'].get('title', 'Physics Concept') if chunks else 'Physics Concept'
    
    # Create Veo 2-optimized scene description prompt
    prompt = f"""Create a 30-second educational video scene description for Google Veo 2 with this EXACT format:

SCENE: [Visual setting and environment description]
NARRATION: [Clear educational narration, ≤50 words]
VISUAL_ACTION: [Specific animations, demonstrations, or visual elements]
CAMERA: [Camera movement and framing details]
AUDIO: [Background sounds, effects, or music cues]

###EDUCATIONAL_CONTENT
Topic: {primary_section}
Content: {combined_text}
Query Context: {user_query if user_query else "General explanation"}
###END

REQUIREMENTS FOR VEO 2:
- SCENE: Describe educational setting (classroom, lab, animated world, etc.)
- NARRATION: ≤50 words, 8th-grade level, active voice, no jargon
- VISUAL_ACTION: Specific animations that illustrate the concept (diagrams appearing, objects moving, transformations)
- CAMERA: Cinematic camera work (close-up, wide shot, tracking, zoom)
- AUDIO: Educational background (soft instrumental, nature sounds, or silence)
- Focus ONLY on {primary_section} concept
- Make it visually engaging and educational
- Use scientific demonstrations, animations, or real-world examples
- Ensure all visual elements support the learning objective

OUTPUT FORMAT:
SCENE: 
NARRATION: 
VISUAL_ACTION: 
CAMERA: 
AUDIO: """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert at creating cinematic educational video scene descriptions for Veo 2. Focus on visual storytelling and educational demonstrations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.7
        )
        
        script = response.choices[0].message.content.strip()
        
        # Validate narration word count and apply retry guard
        narration_count = count_narration_words(script)
        if narration_count > 50:
            # Retry with forced brevity for narration
            shorter_prompt = f"SHORTEN the NARRATION section to exactly ≤50 words while keeping all other sections:\n\n{script}"
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at condensing educational narration while maintaining clarity."},
                    {"role": "user", "content": shorter_prompt}
                ],
                max_tokens=150,
                temperature=0  # Zero temperature for consistent shortening
            )
            script = response.choices[0].message.content.strip()
        
        return script
        
    except Exception as e:
        # Fallback Veo 2 scene description
        return f"""SCENE: Clean, modern educational setting with soft lighting and minimal background
NARRATION: Let's explore {primary_section} and understand this fundamental physics concept clearly.
VISUAL_ACTION: Simple text animation showing key concept with gentle highlighting effects
CAMERA: Medium shot with slow zoom-in for emphasis
AUDIO: Soft instrumental background music at low volume"""


def count_narration_words(script: str) -> int:
    """
    Count words in the NARRATION section only.
    """
    import re
    # Extract only the NARRATION section
    narration_match = re.search(r'NARRATION:\s*(.+?)(?:\n|$)', script, re.DOTALL)
    if narration_match:
        narration_text = narration_match.group(1).strip()
        return len(narration_text.split())
    return 0

def count_words_in_script(script: str) -> int:
    """
    Count words in the entire script, excluding format labels.
    """
    # Remove format labels (SCENE:, NARRATION:, etc.)
    import re
    content_only = re.sub(r'^(SCENE|NARRATION|VISUAL_ACTION|CAMERA|AUDIO):\s*', '', script, flags=re.MULTILINE)
    return len(content_only.split())


def parse_script_sections(script: str) -> Dict[str, str]:
    """
    Parse the Veo 2 script into its components.
    """
    sections = {'SCENE': '', 'NARRATION': '', 'VISUAL_ACTION': '', 'CAMERA': '', 'AUDIO': ''}
    
    import re
    lines = script.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('SCENE:'):
            current_section = 'SCENE'
            sections[current_section] = line[6:].strip()
        elif line.startswith('NARRATION:'):
            current_section = 'NARRATION'
            sections[current_section] = line[10:].strip()
        elif line.startswith('VISUAL_ACTION:'):
            current_section = 'VISUAL_ACTION'
            sections[current_section] = line[14:].strip()
        elif line.startswith('CAMERA:'):
            current_section = 'CAMERA'
            sections[current_section] = line[7:].strip()
        elif line.startswith('AUDIO:'):
            current_section = 'AUDIO'
            sections[current_section] = line[6:].strip()
        elif current_section and line:
            # Continue previous section if line doesn't start with a label
            sections[current_section] += ' ' + line
    
    return sections


def script_to_narration(script: str) -> str:
    """
    Extract just the narration text from Veo 2 script.
    """
    sections = parse_script_sections(script)
    return sections['NARRATION'].strip()

def script_to_veo_prompt(script: str) -> str:
    """
    Convert structured Veo 2 script to a single prompt for video generation.
    """
    sections = parse_script_sections(script)
    
    # Combine all sections into a cohesive Veo 2 prompt
    prompt_parts = []
    
    if sections['SCENE']:
        prompt_parts.append(f"Scene: {sections['SCENE']}")
    
    if sections['VISUAL_ACTION']:
        prompt_parts.append(f"Action: {sections['VISUAL_ACTION']}")
        
    if sections['CAMERA']:
        prompt_parts.append(f"Camera: {sections['CAMERA']}")
        
    if sections['NARRATION']:
        prompt_parts.append(f'Narration: "{sections["NARRATION"]}"')
        
    if sections['AUDIO']:
        prompt_parts.append(f"Audio: {sections['AUDIO']}")
    
    return '. '.join(prompt_parts)


def test_explainer():
    """
    Test function for the Veo 2 script generator.
    """
    print("=== Testing Veo 2 Script Generator ===")
    
    # Test chunks (simulating retriever output)
    test_chunks = [
        {
            'text': "1.3 Accuracy, Precision, and Significant Figures\nAccuracy of a measured value refers to how close a measurement is to the correct value. The uncertainty in a measurement is an estimate of the amount by which the measurement could be wrong.",
            'metadata': {
                'section': '1.3',
                'title': 'Accuracy, Precision, and Significant Figures',
                'chapter': 1
            }
        },
        {
            'text': "The precision of a measurement system refers to how close the agreement is between repeated measurements. Precision is related to the uncertainty in a measurement, which depends on the instrument used.",
            'metadata': {
                'section': '1.3',
                'title': 'Accuracy, Precision, and Significant Figures',
                'chapter': 1
            }
        }
    ]
    
    # Additional test chunks for variety
    motion_chunks = [
        {
            'text': "Newton's First Law states that an object at rest stays at rest and an object in motion stays in motion with the same speed and in the same direction unless acted upon by an unbalanced force.",
            'metadata': {
                'section': '4.1',
                'title': 'Newton\'s First Law of Motion',
                'chapter': 4
            }
        }
    ]
    
    # Test cases with different physics concepts
    test_cases = [
        {
            'chunks': test_chunks,
            'query': "What's the difference between accuracy and precision?",
            'concept': "Measurement Concepts"
        },
        {
            'chunks': motion_chunks,
            'query': "Explain Newton's first law",
            'concept': "Laws of Motion"
        },
        {
            'chunks': test_chunks,
            'query': "",  # Empty query test
            'concept': "Default Explanation"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"TEST {i}: {test_case['concept']}")
        print(f"Query: '{test_case['query']}'")
        print('='*60)
        
        # Generate Veo 2 script
        script = generate_script(test_case['chunks'], test_case['query'])
        
        # Count words
        total_words = count_words_in_script(script)
        narration_words = count_narration_words(script)
        
        print(f"\n📊 METRICS:")
        print(f"   Total words: {total_words}")
        print(f"   Narration words: {narration_words}/50 limit")
        print(f"   Narration status: {'✅ GOOD' if narration_words <= 50 else '❌ TOO LONG'}")
        
        print(f"\n🎬 GENERATED VEO 2 SCRIPT:")
        print(script)
        
        # Parse and display sections
        print(f"\n📋 PARSED SECTIONS:")
        sections = parse_script_sections(script)
        for section_name, content in sections.items():
            if content.strip():
                print(f"   {section_name}: {content}")
        
        # Show Veo 2 prompt conversion
        print(f"\n🎯 VEO 2 PROMPT:")
        veo_prompt = script_to_veo_prompt(script)
        print(f'"{veo_prompt}"')
        
        # Show just narration
        print(f"\n🗣️ NARRATION ONLY:")
        narration = script_to_narration(script)
        print(f'"{narration}"')
        
        print("-" * 60)


if __name__ == "__main__":
    test_explainer()
