from shiny import App, ui, render, reactive
import html

app_ui = ui.page_fluid(
    ui.head_content(
        ui.tags.script(src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"),
        ui.tags.script("""
            function renderMermaid() {
                mermaid.initialize({startOnLoad: false});
                mermaid.run();
            }
        """)
    ),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_text_area("mermaid_code", "Enter Mermaid Code:", 
                               value="graph TD\nA[Client] --> B[Load Balancer]\nB --> C[Server01]\nB --> D[Server02]",
                               height="300px"),
            ui.input_action_button("render", "Render Chart"),
            # open="always",
        ),
        ui.output_ui("mermaid_output")
    )
)

def server(input, output, session):
    @output
    @render.ui
    @reactive.event(input.render)
    def mermaid_output():
        mermaid_code = input.mermaid_code()
        escaped_code = html.escape(mermaid_code)
        return ui.HTML(f"""
            <div class="mermaid">
                {escaped_code}
            </div>
            <script>
                renderMermaid();
            </script>
        """)

app = App(app_ui, server)
