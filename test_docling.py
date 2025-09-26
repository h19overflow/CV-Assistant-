#!/usr/bin/env python3

import logging
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_docling_conversion():
    # Set up converter
    pipeline_options = PdfPipelineOptions()
    pipeline_options.allow_external_plugins = True
    pipeline_options.do_ocr = True

    converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(
                pipeline_options=pipeline_options
            )
        }
    )

    file_path = r"C:\Users\User\Projects\Resume_System\src\backend\core\pipelines\cv_analysis\core\DATABASE-SCHEMA.pdf"

    try:
        result = converter.convert(file_path)

        print(f"Conversion result type: {type(result)}")
        print(f"Document type: {type(result.document)}")
        print(f"Number of pages: {len(result.document.pages)}")

        # Check pages structure
        if result.document.pages:
            print(f"Pages type: {type(result.document.pages)}")
            print(f"Pages keys/indices: {list(result.document.pages.keys()) if hasattr(result.document.pages, 'keys') else 'Not a dict'}")

            # Get first page (try different access methods)
            first_page = None
            if isinstance(result.document.pages, dict):
                first_key = list(result.document.pages.keys())[0]
                first_page = result.document.pages[first_key]
                print(f"First page key: {first_key}")
            elif isinstance(result.document.pages, list):
                first_page = result.document.pages[0]

            if first_page:
                print(f"First page type: {type(first_page)}")
                print(f"Available methods: {[m for m in dir(first_page) if not m.startswith('_')]}")

                # Try to get text
                try:
                    text = first_page.export_to_text()
                    print(f"First page text length: {len(text)}")
                    print(f"First 200 chars: '{text[:200]}'")
                except Exception as e:
                    print(f"Error getting page text: {e}")

        # Check document methods
        print(f"Document methods: {[m for m in dir(result.document) if not m.startswith('_')]}")

        # Try whole document
        try:
            full_text = result.document.export_to_text()
            print(f"Full document text length: {len(full_text)}")
            print(f"First 200 chars: '{full_text[:200]}'")
        except Exception as e:
            print(f"Error getting document text: {e}")

        # Try getting text through other methods
        try:
            # Check if there's a text attribute
            if hasattr(result.document, 'text'):
                print(f"Document has text attribute: {len(result.document.text)}")

            # Check content
            if hasattr(result.document, 'content'):
                print(f"Document has content attribute: {type(result.document.content)}")

            # Check raw content
            if hasattr(result.document, 'export_to_markdown'):
                markdown = result.document.export_to_markdown()
                print(f"Markdown length: {len(markdown)}")
                print(f"First 200 chars of markdown: '{markdown[:200]}'")

        except Exception as e:
            print(f"Error trying alternative methods: {e}")

    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_docling_conversion()