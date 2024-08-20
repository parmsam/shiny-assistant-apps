from shiny import App, reactive, render, ui
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

app_ui = ui.page_fluid(
    ui.card(
        ui.card_header("Mood Tracker"),
        ui.input_date("log_date", "Date", value=date.today()),
        ui.input_select("mood", "Mood", choices=["Very Happy", "Happy", "Neutral", "Sad", "Very Sad"]),
        ui.input_text("notes", "Notes (optional)", placeholder="Enter any notes for the day"),
        ui.input_action_button("add", "Log Mood"),
        ui.tags.hr(),
        ui.output_table("mood_log"),
        ui.tags.hr(),
        ui.input_date_range("date_range", "Select Date Range for Trend"),
        ui.output_plot("mood_trend")
    )
)

def server(input, output, session):
    moods = reactive.Value(pd.DataFrame(columns=["Date", "Mood", "Notes"]))

    @reactive.Effect
    @reactive.event(input.add)
    def add_mood():
        new_mood = pd.DataFrame({
            "Date": [input.log_date()],
            "Mood": [input.mood()],
            "Notes": [input.notes()]
        })
        updated_moods = pd.concat([moods.get(), new_mood], ignore_index=True)
        updated_moods = updated_moods.drop_duplicates(subset=["Date"], keep="last")
        updated_moods = updated_moods.sort_values(by="Date", ascending=False)
        moods.set(updated_moods)
        ui.update_text("notes", value="")

    @output
    @render.table
    def mood_log():
        df = moods.get()
        return df  # Return the DataFrame directly

    @output
    @render.plot
    def mood_trend():
        df = moods.get()
        if df.empty:
            return plt.figure()

        start_date = input.date_range()[0] or df["Date"].min()
        end_date = input.date_range()[1] or df["Date"].max()

        df = df[(df["Date"] >= start_date) & (df["Date"] <= end_date)]
        df["Date"] = pd.to_datetime(df["Date"])
        df = df.sort_values(by="Date")

        mood_mapping = {"Very Happy": 5, "Happy": 4, "Neutral": 3, "Sad": 2, "Very Sad": 1}
        df["Mood_Value"] = df["Mood"].map(mood_mapping)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df["Date"], df["Mood_Value"], marker="o")
        ax.set_ylim(0.5, 5.5)
        ax.set_yticks(range(1, 6))
        ax.set_yticklabels(["Very Sad", "Sad", "Neutral", "Happy", "Very Happy"])
        ax.set_xlabel("Date")
        ax.set_ylabel("Mood")
        ax.set_title("Mood Trend Over Time")
        plt.xticks(rotation=45)
        plt.tight_layout()
        return fig

app = App(app_ui, server)
