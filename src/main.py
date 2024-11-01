from pathlib import Path
import gradio as gr
from typing import List, Any, Dict
import os
import logging
import base64
import mimetypes
import requests
from PIL import Image
from io import BytesIO

MARKER_API_URL = "http://dls006.idc.ctbto.org:3006"

def decode_base64_to_pil(base64_str):
    return Image.open(BytesIO(base64.b64decode(base64_str)))


parse_document_docs = {
    "curl": """curl -X POST -F "file=@/path/to/document" http://localhost:8000/parse_document""",
    "python": """
    coming soon⌛
    """,
    "javascript": """
    coming soon⌛
    """,
}


def parse_document(input_file_path, parameters, request: gr.Request):
    # Validate file extension
    allowed_extensions = [".pdf", ".ppt", ".pptx", ".doc", ".docx"]
    file_extension = os.path.splitext(input_file_path)[1].lower()
    if file_extension not in allowed_extensions:
        raise gr.Error(f"File type not supported: {file_extension}")
    try:
        host_url = request.headers.get("host")

        post_url = f"{MARKER_API_URL}/convert?max_pages=30&batch_multiplier=8"
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

        # Decode each base64-encoded image to a PIL image
        pil_images = [
            decode_base64_to_pil(images[image_name]) for image_name in images
        ]

        return (
            str(document_response["markdown"]),
            gr.Gallery(value=pil_images, visible=True),
            str(document_response["markdown"]),
            gr.JSON(value=document_response, visible=True),
        )

    except Exception as e:
        raise gr.Error(f"Failed to parse: {e}")


demo_ui = gr.Blocks(theme=gr.themes.Monochrome(radius_size=gr.themes.sizes.radius_none))

with demo_ui as demo:
    gr.Markdown(
        "<h1>Marker-API</h1> \n Easily deployable 🚀 API to convert PDF to markdown quickly with high accuracy."
    )

    with gr.Tabs():
        with gr.TabItem("Documents"):
            with gr.Row():
                with gr.Column(scale=80):
                    document_file = gr.File(
                        label="Upload Document",
                        type="filepath",
                        file_count="single",
                        interactive=True,
                        file_types=[".pdf", ".ppt", ".doc", ".pptx", ".docx"],
                    )
                    with gr.Accordion("Parameters", visible=True):
                        document_parameter = gr.Dropdown(
                            [
                                "Fixed Size Chunking",
                                "Regex Chunking",
                                "Semantic Chunking",
                            ],
                            label="Chunking Stratergy",
                        )
                        if document_parameter == "Fixed Size Chunking":
                            document_chunk_size = gr.Number(
                                minimum=250, maximum=10000, step=100, show_label=False
                            )
                            document_overlap_size = gr.Number(
                                minimum=250, maximum=1000, step=100, show_label=False
                            )
                    document_button = gr.Button("Parse Document")
                with gr.Column(scale=200):
                    with gr.Accordion("Markdown"):
                        document_markdown = gr.Markdown()
                    with gr.Accordion("Extracted Images"):
                        document_images = gr.Gallery(visible=False)
                    with gr.Accordion("Chunks", visible=False):
                        document_chunks = gr.Markdown()
            with gr.Accordion("JSON Output"):
                document_json = gr.JSON(label="Output JSON", visible=False)
            with gr.Accordion("Use API", open=True):
                gr.Code(
                    language="shell",
                    value=parse_document_docs["curl"],
                    lines=1,
                    label="Curl",
                )
                gr.Code(
                    language="python", value="Coming Soon⌛", lines=1, label="python"
                )


    document_button.click(
        fn=parse_document,
        inputs=[document_file, document_parameter],
        outputs=[document_markdown, document_images, document_chunks, document_json],
    )

    
if __name__ == "__main__":
    demo.queue(max_size=10)
    demo.launch(server_name="0.0.0.0")