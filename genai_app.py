import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from google import genai
from dotenv import load_dotenv
import gradio as gr

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize the Gemini client
client = genai.Client(api_key=GEMINI_API_KEY)

# Initialize FastAPI app
app = FastAPI(title="Summarizer API", version="1.0")

# Request and response models
class SummaryRequest(BaseModel):
    text: str
    max_length: Optional[int] = 150

class SummaryResponse(BaseModel):
    summary: str

def generate_summary(text: str, max_length: int = 150) -> str:
    prompt = f"Summarize the following text briefly in under {max_length} words:\n\n{text}"
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return response.text.strip()

@app.post("/summarize", response_model=SummaryResponse)
def summarize(request: SummaryRequest):
    try:
        summary = generate_summary(request.text, request.max_length)
        return {"summary": summary}
    except Exception as e:
        print(f"Error during summarization: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def summarize_ui(text: str, max_length: int):
    if not text.strip():
        raise gr.Error("Please enter some text to summarize.")
    try:
        return generate_summary(text, int(max_length))
    except Exception as e:
        raise gr.Error(f"Error during summarization: {e}")

with gr.Blocks(title="GenAI Summarizer") as demo:
    gr.Markdown("# 📝 GenAI Summarizer\nPaste text below and get a concise, AI-generated summary powered by Gemini.")
    with gr.Row():
        with gr.Column():
            input_text = gr.Textbox(
                label="Text to summarize",
                placeholder="Paste your article, notes, or transcript here...",
                lines=14,
            )
            max_length = gr.Slider(
                minimum=20, maximum=500, value=150, step=10,
                label="Max summary length (words)",
            )
            with gr.Row():
                clear_btn = gr.ClearButton([input_text])
                submit_btn = gr.Button("Summarize", variant="primary")
        with gr.Column():
            output_text = gr.Textbox(label="Summary", lines=14, interactive=False, show_copy_button=True)

    submit_btn.click(fn=summarize_ui, inputs=[input_text, max_length], outputs=output_text)
    input_text.submit(fn=summarize_ui, inputs=[input_text, max_length], outputs=output_text)

app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8000)))