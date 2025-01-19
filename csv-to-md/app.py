from shiny import App, ui, render, reactive
import pandas as pd
import io

app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_file("file", "Choose CSV file"),
        ui.input_checkbox("header", "File has header", True),
    ),
    ui.navset_card_tab(
        ui.nav_panel("Code",
            ui.card(
                    ui.card_header("Markdown Table Code"),
                    ui.input_action_button("copy", "Copy to Clipboard", class_="btn-primary"),
                    ui.output_text("markdown_code"),
            ),
        ),
        ui.nav_panel("Rendered",
            ui.card(
                ui.card_header("Rendered Table"),
                ui.output_ui("rendered_table"),
            ),
        ),
    ),
    ui.tags.script(
        """
        $(function() {
            Shiny.addCustomMessageHandler("copy_to_clipboard", function(message) {
                navigator.clipboard.writeText(message.text);
            });
        });
        """
    ),
)

def server(input, output, session):
    
    def create_markdown_table(df, header=True):
        # Convert DataFrame to markdown table
        lines = []
        
        # Add header
        if header:
            lines.append("| " + " | ".join(str(col) for col in df.columns) + " |")
            lines.append("| " + " | ".join(["---"] * len(df.columns)) + " |")
        
        # Add data rows
        for _, row in df.iterrows():
            lines.append("| " + " | ".join(str(val) for val in row) + " |")
            
        return "\n".join(lines)

    @output
    @render.text
    def markdown_code():
        if not input.file():
            return "Upload a CSV file to see the markdown table code"
        
        file_data = input.file()[0]["datapath"]
        df = pd.read_csv(file_data)
        
        return create_markdown_table(df, input.header())

    @output
    @render.ui
    def rendered_table():
        if not input.file():
            return "Upload a CSV file to see the rendered table"
        
        file_data = input.file()[0]["datapath"]
        df = pd.read_csv(file_data)
        
        return ui.HTML(f"<div class='table-responsive'>{df.to_html(index=False)}</div>")

    @reactive.effect
    @reactive.event(input.copy)
    async def _():
        if input.input_text():
            ui.notification_show("Text copied to clipboard!", duration=3)
            await session.send_custom_message("copy_to_clipboard", {"text": input.input_text()})
        else:
            ui.notification_show("No text to copy!", type="warning", duration=3)
    
    @output
    @render.ui
    def copy_status():
        return 
            
app = App(app_ui, server)