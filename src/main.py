from pathlib import Path
import gradio as gr
import base64
import mimetypes
import requests
from PIL import Image
from io import BytesIO
import shutil
import re
import os
from urllib.parse import quote

MARKER_API_URL = "https://marker-api.example.com"
GRADIO_TEMP_DIR = "data"

MARKER_HEADER = """
# Marker UI
**Marker** is a state-of-the-art PDF to Markdown Converter.  
"""

MARKER_ABOUT = """
## About
Marker is a state-of-the-art PDF to Markdown converter that uses OCR to extract text and images from PDFs.

## How to Use
1. Upload a PDF, PPT, or DOC file.
2. Click on "Convert Document".
3. View the extracted Markdown and images.

## Documentation
- [Marker](https://github.com/VikParuchuri/marker)
- [Marker API Documentation](https://github.com/adithya-s-k/marker-api)
"""

def zip_folder(source_folder, output_path):
   shutil.make_archive(output_path, 'zip', source_folder)
   return Path(f"{output_path}.zip")

def decode_base64_to_pil(base64_str):
    return Image.open(BytesIO(base64.b64decode(base64_str)))

def download_file():
    return [gr.UploadButton(visible=True), gr.DownloadButton(visible=True)]

def parse_document(input_file_path):
    # Validate file extension
    allowed_extensions = [".pdf", ".ppt", ".pptx", ".doc", ".docx"]
    file_extension = os.path.splitext(input_file_path)[1].lower()
    if file_extension not in allowed_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")
    try:
        marker_api_url = os.environ.get("MARKER_API_URL", MARKER_API_URL)
        post_url = f"{marker_api_url}/convert?max_pages=30&batch_multiplier=8"
        # Determine the MIME type of the file
        mime_type, _ = mimetypes.guess_type(input_file_path)
        if not mime_type:
            mime_type = "application/octet-stream"  # Default MIME type if not found

        with open(input_file_path, "rb") as f:
            files = {"pdf_file": (input_file_path, f, mime_type)}
            response = requests.post(
                post_url, files=files, headers={"accept": "application/json"}
            )

        document_response = response.json()["result"]
        images = document_response.get("images", [])
        input_file_path = Path(input_file_path)
        zip_dir = input_file_path.parent/input_file_path.stem
        zip_dir.mkdir(exist_ok=True)
        file_md = zip_dir / f"{input_file_path.stem}.md"
        with open(file_md, "w") as f:
            f.write(document_response["markdown"])
        for image_name in images:
            image_path = zip_dir / image_name
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(images[image_name]))
        image_dir = quote("/".join(str(zip_dir).split("/")[-3:]))
        zip_file = zip_folder(zip_dir, zip_dir)
        document_response["markdown"] = re.sub(r"(\n![^(]+)\(([^)]+)\)", fr"\1(/gradio_api/file={image_dir}/\2)", document_response["markdown"])
        return (
            str(document_response["markdown"]),
            gr.DownloadButton(
                label=f"Download {zip_file.name}",
                value=zip_file,
                visible=True,
            ),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")

os.environ["GRADIO_TEMP_DIR"] = GRADIO_TEMP_DIR
marker_ui = gr.Blocks(theme=gr.themes.Monochrome(radius_size=gr.themes.sizes.radius_none))

with marker_ui:
    gr.set_static_paths(paths=["assets", GRADIO_TEMP_DIR])
    gr.Markdown(MARKER_HEADER)
    with gr.Tabs():
        with gr.TabItem("Documents"):
            with gr.Column(scale=80):
                document_file = gr.File(
                    label="Upload Document",
                    type="filepath",
                    file_count="single",
                    interactive=True,
                    file_types=[".pdf", ".ppt", ".doc", ".pptx", ".docx"],
                )
                document_button = gr.Button("Convert Document")
                download_button = gr.DownloadButton("Download the markdown file and its images", visible=True)
            with gr.Column(scale=200):
                with gr.Accordion("Markdown", open=True):
                    document_markdown = gr.Markdown(min_height=200, container=False)
        with gr.TabItem("About"):
            gr.Markdown(MARKER_ABOUT)
    document_button.click(
        fn=parse_document,
        inputs=[document_file],
        outputs=[document_markdown, download_button],
    )
    download_button.click(download_file, None, [document_button, download_button])

    
if __name__ == "__main__":
    marker_ui.queue(max_size=10)
    marker_ui.launch(server_name="0.0.0.0", server_port=8000)