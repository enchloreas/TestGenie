# app/ui_testgenie.py
from .config import settings
import gradio as gr
from .ai_service import AIService

# Initialize the AIService
ai_service = AIService(
    jira_domain=settings.JIRA_DOMAIN,
    jira_email=settings.JIRA_EMAIL,
    jira_api_token=settings.JIRA_API_TOKEN,
    openrouter_url=settings.OPENROUTER_URL,
    openrouter_api_key=settings.OPENROUTER_API_KEY
)

"""
# Fake function to simulate test case generation
def fake_generate(project, issue, model, temperature, max_tokens):
    if not project.strip():
        return "", gr.update(value="Project Key is required.", visible=True)
    if not issue.strip():
        return "", gr.update(value="Issue Key is required.", visible=True)
    # If all fields are filled, proceed
    return "✅ Successfully generated: Example test cases.", gr.update(value="", visible=False)"""

# New function to generate test cases
def generate_test_cases(project, issue, model, temperature, max_tokens):
    if not project.strip():
        return "", gr.update(value="Project Key is required.", visible=True)
    if not issue.strip():
        return "", gr.update(value="Issue Key is required.", visible=True)

    try:
        # Call the real generation function
        result = ai_service.generate_and_normalize_test_cases(
            issue_key=issue.strip(),
            model=model,
            temperature=float(temperature),
            max_tokens=int(max_tokens)
        )

        return (
                result,
                gr.update(value="", visible=False),
                gr.update(value="Generated successfully", visible=True, elem_id="generate-status-success")
            )
    except Exception as e:
        return (
                "",
                gr.update(value=f"Generation failed: {str(e)}", visible=True),
                gr.update(value=f"Generation failed: {str(e)}", visible=True, elem_id="generate-status-fail")
            )
    
# Fake function to simulate Jira submission
def fake_submit():
    return "✅ Successfully submitted to Jira."

with gr.Blocks(
    css="""
#error-message, #error-message * {
    color: red !important;
    margin-top: 4px;
}

#generate-status-success {
    color: green !important;
    font-weight: bold;
}

#generate-status-fail {
    color: red !important;
    font-weight: bold;
}
/* Hide expand, download, and fullscreen icons on the image */
#tg-logo button[aria-label="Download"],
#tg-logo button[aria-label="Expand"],
#tg-logo button[aria-label="Fullscreen"],
#tg-logo .svelte-1ipelgc,
#tg-logo .absolute {
    display: none !important;
}
"""
) as demo:
    # Top header with logo and title
    with gr.Row():
        with gr.Column():
            gr.Image(
                value="assets/TGToolbar.png",
                show_label=False,
                container=False,
                elem_id="tg-logo"
            )
    # Input fields: Project and Issue keys
    with gr.Row():
        project = gr.Textbox(label="Project Key (e.g. TG) *", interactive=True)
        issue = gr.Textbox(label="Issue Key (e.g. TG-1) *", interactive=True)
    error_message = gr.Markdown("", visible=False, elem_id="error-message")

    # Dropdown for model selection
    with gr.Row(scale=2):
        model = gr.Dropdown(
            label="Model",
            choices=["meta-llama/llama-3-8b-instruct", "gpt-4", "mistral-7b-instruct", "other"],
            value="meta-llama/llama-3-8b-instruct"
        )

    # Fields for temperature and max_tokens
    with gr.Row():
        temperature = gr.Textbox(label="Temperature (e.g. 0.7)", value="0.7")
        max_tokens = gr.Textbox(label="Max Tokens (e.g. 1000)", value="1000")

    # Button to generate test cases
    generate_button = gr.Button("Generate Test Cases")

    # Status message after generation
    generate_status = gr.Markdown("⏳ Waiting to generate...")

    # Output area to show generated test cases
    generated_test_cases = gr.Textbox(label="Generated Test Cases", lines=10)

    # Button to submit test cases to Jira
    submit_button = gr.Button("Submit to Jira", scale=2)

    # Status message after submission
    submit_status = gr.Markdown("⏳ Waiting for submit...")

    # Connect fake functions to buttons
    generate_button.click(
        fn=generate_test_cases,
        inputs=[project, issue, model, temperature, max_tokens],
        outputs=[generated_test_cases, error_message, generate_status]
    )
    submit_button.click(fn=fake_submit, outputs=[submit_status])

# Launch the Gradio UI
demo.launch(inbrowser=True)
