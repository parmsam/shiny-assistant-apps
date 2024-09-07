from shiny import App, ui, render, reactive
from gtts import gTTS
import os
import base64

app_ui = ui.page_fluid(
    ui.card(
        ui.input_text("user_input", "Enter some text:"),
        ui.input_action_button("speak", "Speak"),
        ui.output_ui("audio_output")
    )
)

def server(input, output, session):
    @reactive.Effect
    @reactive.event(input.speak)
    def speak_text():
        text = input.user_input()
        if text:
            tts = gTTS(text=text, lang='en')
            tts.save("speech.mp3")
            
    @render.ui
    @reactive.event(input.speak)
    def audio_output():
        if os.path.exists("speech.mp3"):
            with open("speech.mp3", "rb") as audio_file:
                encoded = base64.b64encode(audio_file.read()).decode()
            return ui.tags.audio(
                ui.tags.source(src=f"data:audio/mp3;base64,{encoded}", type="audio/mp3"),
                controls=True
            )
        return ui.p("Click 'Speak' to hear the text.")

app = App(app_ui, server)
