import json
import gradio as gr
from main import analyze, extract_text_from_file
from config import ModelConfig

def run_analysis(text: str = None, file_path: str = None):
    """Analyze text, URL, or uploaded file"""
    # Determine input source
    if file_path:
        # Extract text from uploaded file
        extracted = extract_text_from_file(file_path)
        if extracted.startswith("Error:"):
            return json.dumps({"error": extracted}, indent=2, ensure_ascii=False)
        input_data = extracted
    elif text and text.strip():
        input_data = text
    else:
        return json.dumps({"error": "Please enter text or upload a file."}, indent=2, ensure_ascii=False)

    try:
        result = analyze(input_data)
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2, ensure_ascii=False)


# Create Gradio interface
with gr.Blocks(title="Multilingual Intelligence Analyzer") as demo:
    gr.Markdown("# Indian Multilingual Intelligence Analyzer")
    gr.Markdown(f"**Model:** {ModelConfig.MODEL_NAME}")
    gr.Markdown("Analyze text in any Indic language or English. Supports NER, translation, sentiment analysis, and more.")
    gr.Markdown("**Supports:** Direct text input and file upload (JPG, PNG, PDF, DOCX, TXT)")
    
    with gr.Row():
        with gr.Column():
            gr.Markdown("## Input Options")
            
            input_text = gr.Textbox(
                label="📝 Text Input",
                placeholder="Paste text (e.g., social media posts, reviews) here...",
                lines=8
            )
            
            gr.Markdown("### OR")
            
            file_upload = gr.File(
                label="📄 Upload File",
                type="filepath",
                file_count="single",
                file_types=["image", ".pdf", ".docx", ".txt"]
            )
            
            gr.Markdown("**Supported formats:**\n- Images: JPG, PNG, BMP, TIFF\n- Documents: PDF, DOCX, TXT")
            
            analyze_btn = gr.Button("🔍 Analyze", variant="primary", size="lg")
        
        with gr.Column():
            output = gr.Code(
                label="📊 Analysis Output (JSON)",
                language="json",
                lines=35
            )
    
    gr.Markdown("---")
    gr.Markdown("### Example Inputs:")
    gr.Examples(
        examples=[
            ["OMG!! 😱 @Apple_India புது #iPhone16Pro ஆர்டர் பண்ணிட்டேன்!!! $499 சும்மா கிடையாது bro", None],
            ["नमस्ते! मैं @Microsoft_India से नया Surface Pro खरीदना चाहता हूं। लेकिन @Amazon_IN पर स्टॉक नहीं है।", None],
            ["Hello! I want to buy iPhone 15 Pro from Apple India. But Amazon India is out of stock.", None],
        ],
        inputs=[input_text, file_upload],
        outputs=output,
        fn=run_analysis,
        cache_examples=False,
    )
    
    analyze_btn.click(
        run_analysis,
        inputs=[input_text, file_upload],
        outputs=output
    )


if __name__ == "__main__":
    demo.launch()