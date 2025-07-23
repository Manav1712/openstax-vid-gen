import fitz  # PyMuPDF

# Input and output file paths
input_pdf = "sample_physics.pdf"
output_pdf = "sample_physics_cropped.pdf"
start_page = 18  # 1-indexed (inclusive)
end_page = 117   # 1-indexed (inclusive)

# Open the input PDF
with fitz.open(input_pdf) as doc:
    # PyMuPDF uses 0-based indexing for pages
    selected_pages = list(range(start_page - 1, end_page))
    new_doc = fitz.open()
    for page_num in selected_pages:
        new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
    new_doc.save(output_pdf)
    new_doc.close()

print(f"Cropped PDF saved as {output_pdf} (pages {start_page}-{end_page})") 