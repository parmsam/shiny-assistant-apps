from shiny import App, render, ui
import qrcode
from io import BytesIO
import base64

app_ui = ui.page_fluid(
    ui.card(
        ui.input_text("text", "Enter text for QR code:", value="Hello, World!"),
        ui.output_ui("qr_code"),
    )
)

def server(input, output, session):
    @render.ui
    def qr_code():
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(input.text())
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save image to BytesIO object
        buf = BytesIO()
        img.save(buf)
        
        # Encode image to base64
        img_str = base64.b64encode(buf.getvalue()).decode()
        
        # Return image as an HTML img tag
        return ui.img(src=f"data:image/png;base64,{img_str}", style="width: 300px; height: 300px;")

app = App(app_ui, server)
