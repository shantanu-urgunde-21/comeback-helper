import sys
from pathlib import Path
from src.ingestion.pipeline import IngestionPipeline
from src.ingestion.handwriting_provider import HandwritingOCRProvider
from src.logger import log

def main():
    pdf_path = Path(r"D:\downloads\Lecture_notes_page1.pdf")
    course_name = "Handwritten Coursework"
    
    print("==================================================")
    print(f"Processing PDF: {pdf_path.name}")
    print("==================================================")

    # Initialize Handwriting OCR Provider
    attachments_dir = Path("./.storage/vault") / course_name / "attachments"
    provider = HandwritingOCRProvider(vault_attachments_dir=attachments_dir)
    pipeline = IngestionPipeline(ocr_provider=provider)

    try:
        target_md_path = pipeline.process_pdf(
            pdf_path=pdf_path,
            course_name=course_name
        )

        print("\n==================================================")
        print("EXTRACTION COMPLETED SUCCESSFULLY!")
        print(f"Generated Markdown Note: {target_md_path}")
        print("==================================================")
        
        content = target_md_path.read_text(encoding="utf-8")
        print("\n--- Extracted Markdown Content ---")
        print(content)
        print("-----------------------------------")

    except Exception as e:
        log.error(f"Failed to process PDF: {e}")
        raise e

if __name__ == "__main__":
    main()
