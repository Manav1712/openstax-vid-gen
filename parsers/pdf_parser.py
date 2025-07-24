# pdf_parser.py
# PDF parsing logic for Automated Textbook Explainer Video Generator

import fitz  # PyMuPDF
import re
import json
import tiktoken

SECTION_HEADER_PATTERN = re.compile(r"^(\d+\.\d+) (.+)")
CHAPTER_HEADER_PATTERN = re.compile(r"^CHAPTER (\d+)")

# Use OpenAI's tiktoken for accurate token counting (GPT-3.5/4 encoding)
ENCODING = tiktoken.get_encoding("cl100k_base")
CHUNK_SIZE = 350
CHUNK_OVERLAP = 20


def count_tokens(text):
    return len(ENCODING.encode(text))


def split_into_chunks(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    tokens = ENCODING.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text = ENCODING.decode(chunk_tokens)
        chunks.append(chunk_text)
        if end == len(tokens):
            break
        start += chunk_size - overlap
    return chunks


def extract_hierarchical_chunks(pdf_path):
    doc = fitz.open(pdf_path)
    sections = []
    current_section = None
    current_chapter = None
    section_start_page = None
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        lines = text.splitlines()
        for line in lines:
            chapter_match = CHAPTER_HEADER_PATTERN.match(line.strip())
            if chapter_match:
                current_chapter = int(chapter_match.group(1))
            section_match = SECTION_HEADER_PATTERN.match(line.strip())
            if section_match:
                # Save previous section if exists
                if current_section:
                    current_section['end_page'] = page_num
                    sections.append(current_section)
                section_number = section_match.group(1)
                section_title = section_match.group(2)
                current_section = {
                    'chapter': current_chapter,
                    'section': section_number,
                    'title': section_title,
                    'text': '',
                    'start_page': page_num + 1,  # 1-indexed
                    'end_page': page_num + 1
                }
                section_start_page = page_num + 1
            if current_section:
                current_section['text'] += line + '\n'
    # Save last section
    if current_section:
        sections.append(current_section)

    # Now split each section into leaf chunks
    leaf_chunks = []
    for section in sections:
        section_text = section['text']
        chunks = split_into_chunks(section_text)
        for idx, chunk_text in enumerate(chunks):
            leaf_chunks.append({
                'chapter': section['chapter'],
                'section': section['section'],
                'title': section['title'],
                'chunk_index': idx,
                'text': chunk_text,
                'start_page': section['start_page'],
                'end_page': section['end_page']
            })
    return leaf_chunks


def save_chunks_to_json(chunks, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    pdf_path = "sample_physics_cropped.pdf"
    output_json = "sample_physics_cropped_leaf_chunks.json"
    chunks = extract_hierarchical_chunks(pdf_path)
    save_chunks_to_json(chunks, output_json)
    print(f"Extracted {len(chunks)} leaf chunks and saved to {output_json}") 