from shiny import App, Inputs, Outputs, Session, render, ui, reactive
from openai import OpenAI
import requests
from bs4 import BeautifulSoup
import os
import asyncio

api_key1 = os.getenv("OPENAI_API_KEY")
test_url = "https://posit.co/blog/announcing-the-2024-shiny-contest/"
model_options = ["gpt-3.5-turbo", "gpt-4o-mini", "gpt-4o", "gpt-4",]

app_ui = ui.page_fluid(
    ui.layout_sidebar( 
        ui.sidebar(
            ui.input_password("api_key", "Enter your OpenAI API key:", value=api_key1),
            ui.input_select("model", "Select OpenAI model:", 
                            choices = model_options, 
                            selected = "gpt-3.5-turbo"),
            ui.input_text("url", "Enter webpage URL:", value = test_url),
            ui.input_action_button("convert", "Convert to Quarto"),
            open="always",
        ),
        ui.panel_title("Webpage to Quarto Converter"),
        ui.markdown(
                """This app converts webpage content into a Quarto document using OpenAI's GPT-3.5 turbo model (by default). 
                Enter the URL of the webpage and your OpenAI API key to get started. You can also select a different OpenAI model if needed.
                """,
        ),
        ui.download_button("download", "Download Quarto Document"),
        ui.output_text_verbatim("quarto_output"),
    )
)

def server(input, output, session):
    quarto_content = reactive.Value("")

    @reactive.Effect
    @reactive.event(input.convert)
    def _():
        url = input.url()
        api_key = input.api_key()
        
        if not api_key:
            ui.notification_show("Please enter your OpenAI API key.", type="error")
            return
        
        if url and api_key:
            client = OpenAI(api_key=api_key)
            # Fetch webpage content
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract text content
            text_content = soup.get_text()

            try:
                # Use OpenAI to convert to Quarto
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", 
                        "content": """You are a highly proficient assistant tasked with converting webpage content into a structured Quarto document.
                        
                        Your primary focus is to extract the main content, avoiding any irrelevant sections such as navigation bars, footers, advertisements, or any extraneous links. The goal is to create a clean, well-formatted document using Quarto's markdown flavor.

                        The following is a reference Quarto document template you should use as a basis:
                ---
                title: "Untitled"
                format: html
                params:
                    source_url:
                ---

                ## Main Content

                Quarto enables you to weave together content and executable code into a finished document. To learn more about Quarto, visit <https://quarto.org>.

                ## Code Embedding

                Include code snippets using fenced code blocks and maintain any original formatting. Ensure all images and links are correctly referenced in the document.""",
                        },
                        {"role": "user", 
                        "content": f"""Please convert the following webpage content into a Quarto document (.qmd). 
                        Extract only the main article or body content, and avoid including navigation menus, footers, sidebars, or any non-essential elements. Ensure that the structure, headings, links, images, and any other relevant formatting are preserved according to Quarto standards.
                        Include the webpage URL in the front matter in the source_url parameter.

                        Webpage content: {text_content}"""}
                    ]
                )

                quarto_content.set(response.choices[0].message.content)
            except Exception as e:
                ui.notification_show(f"Error: {str(e)}", type="error")

    @output
    @render.text
    def quarto_output():
        return quarto_content()

    @output
    @render.download(
        # ensure the filename is unique for each download and corresponds to the URL being converted
        filename=lambda: f"webpage_content_{hash(input.url())}.qmd",
    )
    async def download():
        await asyncio.sleep(0.25)
        yield quarto_content()

app = App(app_ui, server)
