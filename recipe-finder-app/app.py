from shiny import App, ui, render, reactive
import pandas as pd

# Sample recipe data (in a real app, this would be a larger database)
recipes = pd.DataFrame({
    'name': ['Pasta Carbonara', 'Vegetable Stir-Fry', 'Omelette', 'Greek Salad'],
    'ingredients': [
        'pasta,eggs,bacon,cheese',
        'vegetables,soy sauce,garlic,oil',
        'eggs,cheese,vegetables',
        'tomatoes,cucumber,olives,feta cheese'
    ],
    'link': [
        'https://www.bbcgoodfood.com/recipes/ultimate-spaghetti-carbonara-recipe',
        'https://www.bbcgoodfood.com/recipes/vegetable-stir-fry',
        'https://www.bbcgoodfood.com/recipes/basic-omelette',
        'https://www.bbcgoodfood.com/recipes/greek-salad'
    ],
    'nutrition': [
        'https://www.nutritionix.com/food/pasta-carbonara',
        'https://www.nutritionix.com/food/vegetable-stir-fry',
        'https://www.nutritionix.com/food/omelette',
        'https://www.nutritionix.com/food/greek-salad'
    ]
})

app_ui = ui.page_fluid(
    ui.h1("Recipe Finder"),
    ui.p("Enter ingredients you have, separated by commas:"),
    ui.input_text("ingredients", "Ingredients", value="eggs, cheese"),
    ui.input_action_button("find", "Find Recipes"),
    ui.output_ui("recipe_table")
)

def server(input, output, session):
    @reactive.calc
    def matching_recipes():
        user_ingredients = [ing.strip().lower() for ing in input.ingredients().split(',')]
        
        def recipe_match(recipe_ingredients):
            recipe_ing_list = recipe_ingredients.split(',')
            return any(ing in user_ingredients for ing in recipe_ing_list)
        
        return recipes[recipes['ingredients'].apply(recipe_match)]

    @output
    @render.ui
    @reactive.event(input.find)
    def recipe_table():
        matches = matching_recipes()
        if matches.empty:
            return ui.p("No matching recipes found. Try adding more ingredients!")
        
        markdown_content = "| Recipe | Recipe Link | Nutrition Info |\n|--------|-------------|----------------|\n"
        for _, row in matches.iterrows():
            markdown_content += f"| {row['name']} | [View Recipe]({row['link']}) | [View Nutrition]({row['nutrition']}) |\n"
        
        return ui.markdown(markdown_content)

app = App(app_ui, server)
