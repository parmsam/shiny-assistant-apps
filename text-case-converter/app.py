from shiny import App, ui, render, reactive
import re

def to_camel_case(text):
    words = re.findall(r'[A-Za-z0-9]+', text.lower())
    return words[0] + ''.join(word.capitalize() for word in words[1:])

def to_snake_case(text):
    return '_'.join(re.findall(r'[A-Za-z0-9]+', text.lower()))

def to_kebab_case(text):
    return '-'.join(re.findall(r'[A-Za-z0-9]+', text.lower()))

def to_pascal_case(text):
    return ''.join(word.capitalize() for word in re.findall(r'[A-Za-z0-9]+', text))

def to_inverse_case(text):
    return ''.join(c.lower() if c.isupper() else c.upper() for c in text)

def to_alternating_case(text):
    return ''.join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))

def to_reverse_case(text):
    return text[::-1]

def to_vowel_case(text):
    vowels = "aeiouAEIOU"
    return ''.join(c.upper() if c in vowels else c.lower() for c in text)

def to_consonant_case(text):
    vowels = "aeiouAEIOU"
    return ''.join(c.lower() if c in vowels else c.upper() for c in text)

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Text Case Converter"),
        ui.input_text_area("input_text", "Enter your text:", rows=2, width = "100%"),
        ui.layout_columns(
        ui.input_action_button("copy", "Copy to Clipboard", class_="btn-primary"),
        ui.download_button("download", "Download", class_="btn-success"),
        ui.input_action_button("clear", "Clear Input", class_ = "btn-secondary"),
        ),
        ui.layout_columns(
            ui.input_action_button("uppercase", "UPPER CASE", class_="btn-light"),
            ui.input_action_button("lowercase", "lower case", class_="btn-light"),
            ui.input_action_button("titlecase", "Title Case", class_="btn-light"),
            ui.input_action_button("sentencecase", "Sentence case", class_="btn-light"),
            ui.input_action_button("camelcase", "camelCase", class_="btn-light"),
            ui.input_action_button("snakecase", "snake_case", class_="btn-light"),
            ui.input_action_button("kebabcase", "kebab-case", class_="btn-light"),
            ui.input_action_button("pascalcase", "PascalCase", class_="btn-light"),
            ui.input_action_button("inversecase", "InVeRsE cAsE", class_="btn-light"),
            ui.input_action_button("alternatingcase", "AlTeRnAtInG cAsE", class_="btn-light"),
            ui.input_action_button("reversecase", "Reverse Case", class_="btn-light"),
            ui.input_action_button("vowelcase", "Vowel Case", class_="btn-light"),
            ui.input_action_button("consonantcase", "Consonant Case", class_="btn-light"),
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
)

def server(input, output, session):
    @reactive.effect
    @reactive.event(input.uppercase)
    def _():
        ui.update_text_area("input_text", value=input.input_text().upper())

    @reactive.effect
    @reactive.event(input.lowercase)
    def _():
        ui.update_text_area("input_text", value=input.input_text().lower())

    @reactive.effect
    @reactive.event(input.titlecase)
    def _():
        ui.update_text_area("input_text", value=input.input_text().title())

    @reactive.effect
    @reactive.event(input.sentencecase)
    def _():
        ui.update_text_area("input_text", value=input.input_text().capitalize())

    @reactive.effect
    @reactive.event(input.camelcase)
    def _():
        ui.update_text_area("input_text", value=to_camel_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.snakecase)
    def _():
        ui.update_text_area("input_text", value=to_snake_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.kebabcase)
    def _():
        ui.update_text_area("input_text", value=to_kebab_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.pascalcase)
    def _():
        ui.update_text_area("input_text", value=to_pascal_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.inversecase)
    def _():
        ui.update_text_area("input_text", value=to_inverse_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.alternatingcase)
    def _():
        ui.update_text_area("input_text", value=to_alternating_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.reversecase)
    def _():
        ui.update_text_area("input_text", value=to_reverse_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.vowelcase)
    def _():
        ui.update_text_area("input_text", value=to_vowel_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.consonantcase)
    def _():
        ui.update_text_area("input_text", value=to_consonant_case(input.input_text()))

    @reactive.effect
    @reactive.event(input.copy)
    async def _():
        if input.input_text():
            ui.notification_show("Text copied to clipboard!", duration=3)
            await session.send_custom_message("copy_to_clipboard", {"text": input.input_text()})
        else:
            ui.notification_show("No text to copy!", type="warning", duration=3)

    @reactive.effect
    @reactive.event(input.clear)
    def _():
        ui.update_text_area("input_text", value="")
        ui.notification_show("Input cleared!", type="message", duration=3)

    @reactive.effect
    @reactive.event(input.download)
    def _():
        if input.input_text():
            ui.download_text("input_text", "text.txt")
        else:
            ui.notification_show("No text to download!", type="warning", duration=3)
    
    @output
    @render.download(
        filename=lambda: f"converted-case-text.txt",
    )
    async def download():
        yield input.input_text()
        ui.notification_show("Downloaded as text file.", type="message", duration=3)

    @output
    @render.ui
    def copy_status():
        return 

app = App(app_ui, server)
