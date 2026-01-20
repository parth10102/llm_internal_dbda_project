import warnings
warnings.filterwarnings('ignore')

import gradio as gr
import json
import main
import time

def run_pipeline(input_text):
    # Initialize an empty result structure
    current_result = {
        "status": "Initializing...",
        "language_metadata": {},
        "classification": {"domains": []},
        "entities": {"ner": {}}
    }
    yield current_result
    
    # Step 1: Cleaning & Language (Fast)
    current_result["status"] = "Detecting Language..."
    # We call the logic directly to yield parts
    cleaned = main.cleaner.clean_input_text(input_text)
    lang_info = main.lang_process.process_language(cleaned)
    
    current_result["language_metadata"] = lang_info
    current_result["status"] = "Language identified. Extracting domains..."
    yield current_result
    
    # Step 2: Domains & Entities (Medium Speed)
    analysis_text = lang_info.get('transliterated_text') or cleaned
    current_result["classification"]["domains"] = main.domain_recog.analyze_domains(analysis_text)
    current_result["entities"]["ner"] = main.entity_extract.extract_entities(analysis_text)
    
    current_result["status"] = "Generating final summary and sentiment..."
    yield current_result
    
    # Step 3: LLM Synthesis (Slowest)
    # The final call to main.analyze returns the full completed dictionary
    final_data = main.analyze(input_text)
    final_data["status"] = "Complete"
    yield final_data

with gr.Blocks(title="Sentinel NLP", theme=gr.themes.Default()) as demo:
    gr.Markdown("# 🛡️ Sentinel: Unified India-Context NLP")
    
    with gr.Row():
        input_box = gr.Textbox(label="Text or URL Input", placeholder="Paste article text or https://link.com", lines=10)
        output_box = gr.Code(label="Intelligence Output", language="json")
    
    btn = gr.Button("🚀 Run Analysis", variant="primary")
    btn.click(run_pipeline, inputs=input_box, outputs=output_box)

if __name__ == "__main__":
    demo.launch()