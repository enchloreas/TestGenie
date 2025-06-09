# app/ui_testgenie.py

import gradio as gr

# Fake function to simulate test case generation
def fake_generate(project, issue, model, temperature, max_tokens):
    if not project.strip():
        return "", gr.update(value="Project Key is required.", visible=True)
    if not issue.strip():
        return "", gr.update(value="Issue Key is required.", visible=True)
    # If all fields are filled, proceed
    return "✅ Successfully generated: Example test cases.", gr.update(value="", visible=False)

# Fake function to simulate Jira submission
def fake_submit():
    return "✅ Successfully submitted to Jira."

with gr.Blocks(
    css="""
#error-message, #error-message * {
    color: red !important;
    margin-top: 4px;
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
        fn=fake_generate,
        inputs=[project, issue, model, temperature, max_tokens],
        outputs=[generated_test_cases, error_message]
    )
    submit_button.click(fn=fake_submit, outputs=[submit_status])

# Launch the Gradio UI
demo.launch()
