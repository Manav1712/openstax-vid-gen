import os
import openai
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_script(chunks: List[Dict], user_query: str = "") -> str:
    """
    Generate a 30-second educational video script from retrieved chunks.
    
    Args:
        chunks: List of chunk dictionaries with 'text' and 'metadata'
        user_query: Original user question (optional, for context)
        
    Returns:
        String containing the video script (≤75 words)
    """
    
    # Combine chunk texts with context delimiters
    combined_text = "\n\n".join([chunk['text'] for chunk in chunks])
    
    # Get primary section title for focus
    primary_section = chunks[0]['metadata'].get('title', 'Physics Concept') if chunks else 'Physics Concept'
    
    # Create the structured prompt
    prompt = f"""Create a 30-second video script with this EXACT format:

Hook: [engaging opening line]
KeyIdea: [main concept in one sentence]
Explain: [clear explanation with example]
RecapCTA: [quick recap/conclusion]

###CONTEXT
{combined_text}
###END

REQUIREMENTS:
- Total ≤ 75 words; auto-truncate if necessary
- Audience: high-school student; language at 8th-grade readability; no jargon unless defined in same sentence
- Focus only on the concept contained in <<{primary_section}>>; ignore unrelated material
- Write in active voice, present tense; aim for ~140 WPM delivery
- Do not mention you are an AI or reference the textbook directly
- Include visual cues in square brackets when helpful, e.g. [ON-SCREEN: F = m × a]
- User question for context: {user_query if user_query else "Explain this clearly"}

OUTPUT FORMAT:
Hook: 
KeyIdea: 
Explain: 
RecapCTA: """

    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an engaging physics tutor who writes 30-second video scripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=120,
            temperature=0.7
        )
        
        script = response.choices[0].message.content.strip()
        
        # Validate word count and apply retry guard
        word_count = count_words_in_script(script)
        if word_count > 75:
            # Retry with forced brevity
            shorter_prompt = f"SHORTEN: Make this script exactly ≤75 words while keeping the same format:\n\n{script}"
            response = openai.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at creating concise educational content."},
                    {"role": "user", "content": shorter_prompt}
                ],
                max_tokens=100,
                temperature=0  # Zero temperature for consistent shortening
            )
            script = response.choices[0].message.content.strip()
        
        return script
        
    except Exception as e:
        # Fallback structured script
        return f"""Hook: Let's understand this physics concept clearly.
KeyIdea: {primary_section} explains fundamental principles.
Explain: {combined_text[:40]}... This helps us understand the physical world.
RecapCTA: Remember this key concept for real-world applications."""


def count_words_in_script(script: str) -> int:
    """
    Count words in the script, excluding format labels.
    """
    # Remove format labels (Hook:, KeyIdea:, etc.)
    import re
    content_only = re.sub(r'^(Hook|KeyIdea|Explain|RecapCTA):\s*', '', script, flags=re.MULTILINE)
    return len(content_only.split())


def parse_script_sections(script: str) -> Dict[str, str]:
    """
    Parse the structured script into its components.
    """
    sections = {'Hook': '', 'KeyIdea': '', 'Explain': '', 'RecapCTA': ''}
    
    import re
    lines = script.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if line.startswith('Hook:'):
            current_section = 'Hook'
            sections[current_section] = line[5:].strip()
        elif line.startswith('KeyIdea:'):
            current_section = 'KeyIdea'
            sections[current_section] = line[8:].strip()
        elif line.startswith('Explain:'):
            current_section = 'Explain'
            sections[current_section] = line[8:].strip()
        elif line.startswith('RecapCTA:'):
            current_section = 'RecapCTA'
            sections[current_section] = line[9:].strip()
        elif current_section and line:
            # Continue previous section if line doesn't start with a label
            sections[current_section] += ' ' + line
    
    return sections


def script_to_narration(script: str) -> str:
    """
    Convert structured script to continuous narration text.
    """
    sections = parse_script_sections(script)
    narration_parts = [
        sections['Hook'],
        sections['KeyIdea'], 
        sections['Explain'],
        sections['RecapCTA']
    ]
    return ' '.join(part for part in narration_parts if part.strip())


def test_explainer():
    """
    Test function for the script generator.
    """
    print("=== Testing LLM Script Generator with Prompt-Craft Strategy ===")
    
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
    
    # Test queries
    test_queries = [
        "What's the difference between accuracy and precision?",
        "Explain significant figures",
        ""  # Empty query test
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: '{query}' ---")
        script = generate_script(test_chunks, query)
        word_count = count_words_in_script(script)
        
        print(f"Generated Script ({word_count} words):")
        print(script)
        print()
        
        # Show parsed sections
        sections = parse_script_sections(script)
        print("Parsed Sections:")
        for section_name, content in sections.items():
            print(f"  {section_name}: {content}")
        
        print()
        print("Continuous Narration:")
        narration = script_to_narration(script)
        print(f'"{narration}"')
        print("-" * 60)


if __name__ == "__main__":
    test_explainer()
