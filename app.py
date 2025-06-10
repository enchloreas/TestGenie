# app/app.py
from app.config import settings
import gradio as gr
from app.ai_service import AIService

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

# Validation functions for project and issue keys
def validate_project(value):
    if not value.strip():
        return gr.update(visible=True, value="Project Key is required.")
    return gr.update(visible=False, value="")

def validate_issue(value):
    if not value.strip():
        return gr.update(visible=True, value="Issue Key is required.")
    return gr.update(visible=False, value="")

# Function to toggle the generate button based on project and issue keys
def toggle_generate_button(project_value, issue_value):
    is_enabled = bool(project_value.strip()) and bool(issue_value.strip())
    return gr.update(interactive=is_enabled)

# New function to generate test cases
def generate_test_cases(project, issue, model, temperature, max_tokens):
    # Validate project and issue keys
    project_error = ""
    issue_error = ""
    if not project.strip():
        project_error = "Project Key is required."
    if not issue.strip():
        issue_error = "Issue Key is required."
    if project_error or issue_error:
        return "", gr.update(value=project_error, visible=bool(project_error)), gr.update(value=issue_error, visible=bool(issue_error)), gr.update(value="", visible=False)

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
            gr.update(value="", visible=False),
            gr.update(value="✅ Generated successfully", visible=True, elem_id="generate-status-success")
        )
    except Exception as e:
        error_msg = f"Generation failed: {str(e)}"
        return (
            "",
            gr.update(value="", visible=False),
            gr.update(value="", visible=False),
            gr.update(value=error_msg, visible=True, elem_id="generate-status-fail")
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
    # Input fields: Project and Issue keys (on same row, with validation)
    with gr.Row():
        with gr.Column():
            project = gr.Textbox(label="Project Key (e.g. TG) *", interactive=True)
            project_error = gr.Markdown("", visible=False, elem_id="error-message")
        with gr.Column():
            issue = gr.Textbox(label="Issue Key (e.g. TG-1) *", interactive=True)
            issue_error = gr.Markdown("", visible=False, elem_id="error-message")

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
    generate_button = gr.Button("Generate Test Cases", interactive=False)

    # Status message after generation
    generate_status = gr.Markdown("⏳ Waiting to generate...")

    # Output area to show generated test cases
    generated_test_cases = gr.Textbox(label="Generated Test Cases", lines=10)

    # Button to submit test cases to Jira
    submit_button = gr.Button("Submit to Jira", scale=2, interactive=False)

    # Status message after submission
    submit_status = gr.Markdown("⏳ Waiting for submit...")

    # Connect fake functions to buttons
    generate_button.click(
        fn=generate_test_cases, 
        inputs=[project, issue, model, temperature, max_tokens],
        outputs=[generated_test_cases, project_error, issue_error, generate_status]
    )
    submit_button.click(fn=fake_submit, outputs=[submit_status])

    
    
    # Add validation and toggle logic
    # Validate project and issue keys, and toggle the generate button
    project.blur(fn=validate_project, inputs=project, outputs=project_error)
    project.change(fn=toggle_generate_button, inputs=[project, issue], outputs=generate_button)
    project.blur(fn=toggle_generate_button, inputs=[project, issue], outputs=generate_button)
    issue.blur(fn=validate_issue, inputs=issue, outputs=issue_error)
    issue.change(fn=toggle_generate_button, inputs=[project, issue], outputs=generate_button)
    issue.blur(fn=toggle_generate_button, inputs=[project, issue], outputs=generate_button)
# Launch the Gradio UI
demo.launch(inbrowser=True)
