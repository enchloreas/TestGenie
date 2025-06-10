# ui_testgenie.py
import gradio as gr
import os

# Path to logo
logo_path = os.path.join(os.path.dirname(__file__), "assets", "LogoTGmini.png")

# Fake logic for testing UI
def fake_generate(*args):
    return "✅ Сгенерировано успешно: пример тест-кейсов."

def fake_submit():
    return "✅ Успешно отправлено в Jira."

with gr.Blocks(css="""
    .centered-logo img {
        display: block;
        margin-left: auto;
        margin-right: auto;
        max-width: 120px;
    }
    .main-title {
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 20px;
    }
""") as demo:
    # Centered logo and title
    with gr.Column():
        gr.Image(value=logo_path, elem_classes="centered-logo", show_label=False, interactive=False)
        gr.Markdown("TestGenie — AI Test Case Generator", elem_classes="main-title")

    # Input fields
    with gr.Row():
        project = gr.Textbox(label="Project Key (e.g. TG)")
        issue = gr.Textbox(label="Issue Key (e.g. TG-1)")

    with gr.Row():
        model = gr.Dropdown(
            label="Model",
            choices=["meta-llama/llama-3-8b-instruct", "gpt-4", "mistral-7b-instruct", "other"],
            value="meta-llama/llama-3-8b-instruct"
        )

    with gr.Row():
        temperature = gr.Textbox(label="Temperature (e.g. 0.7)", value="0.7")
        max_tokens = gr.Textbox(label="Max Tokens (e.g. 1000)", value="1000")

    generate_button = gr.Button("Generate Test Cases")
    generate_status = gr.Markdown("⏳ Waiting to generate...")
    generated_test_cases = gr.Textbox(label="Generated Test Cases", lines=10)

    submit_button = gr.Button("Submit to Jira")
    submit_status = gr.Markdown("⏳ Waiting for submit...")

    # Bind fake functions
    generate_button.click(fn=fake_generate, inputs=[project, issue, model, temperature, max_tokens], outputs=[generated_test_cases])
    submit_button.click(fn=fake_submit, outputs=[submit_status])

demo.launch()
