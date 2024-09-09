from shiny import App, ui, render, reactive

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Tip Calculator"),
        ui.input_numeric("bill", "Total Bill Amount ($)", value=50, min=0, step=0.01),
        ui.input_slider("tip_percent", "Tip Percentage", min=0, max=30, value=15, step=1),
        ui.input_numeric("people", "Number of People", value=1, min=1, step=1),
        ui.output_text("tip_amount"),
        ui.output_text("total_amount"),
        ui.output_text("per_person"),
    )
)

def server(input, output, session):
    @reactive.calc
    def calculate_tip():
        bill = input.bill()
        tip_percent = input.tip_percent() / 100
        people = input.people()

        tip = bill * tip_percent
        total = bill + tip
        per_person = total / people

        return {
            "tip": tip,
            "total": total,
            "per_person": per_person
        }

    @output
    @render.text
    def tip_amount():
        result = calculate_tip()
        return f"Tip Amount: ${result['tip']:.2f}"

    @output
    @render.text
    def total_amount():
        result = calculate_tip()
        return f"Total Amount: ${result['total']:.2f}"

    @output
    @render.text
    def per_person():
        result = calculate_tip()
        return f"Amount Per Person: ${result['per_person']:.2f}"

app = App(app_ui, server)
