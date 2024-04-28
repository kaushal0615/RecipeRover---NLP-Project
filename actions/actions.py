from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List, Tuple
import pandas as pd
from gensim.models import Word2Vec
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_md")

# For the dataset CSV
data = pd.read_csv('/home/kaushalpancholi/Desktop/NLP-Project/RecipeRover/data/IndianFoodDatasetCSV.csv')

# For the Word2Vec model
model = Word2Vec.load('/home/kaushalpancholi/Desktop/NLP-Project/word2vec_ingredients.model', mmap='r')

class ActionRecommendRecipe(Action):
    def name(self) -> Text:
        return "action_recommend_recipe"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        message = "I'm not sure what you are asking for."  # Default message assignment
        user_message = tracker.latest_message.get('text')
        ingredient = self.extract_ingredient(user_message)
        if ingredient:
            recommended_recipes = self.recommend_recipes(ingredient)
            if recommended_recipes:
                # Start building the message with an introductory line
                message_lines = ["Here are some recipes you might like:"]
                
                # Add each recipe name and instructions to the message
                for name, instructions in recommended_recipes:
                    message_lines.append(f"\n{name}")
                    message_lines.append(f"\nInstructions:\n{instructions}")
                
                # Join all the lines into a single message string with new lines
                message = "\n".join(message_lines)
            else:
                message = "I found no recipes for that ingredient. Try another one?"
        else:
            message = "I don't recognize that ingredient. Can you try another one?"
        dispatcher.utter_message(text=message)
        return []
    
    def extract_ingredient(self, text: Text) -> Text:
        # Perform dependency parsing
        doc = nlp(text)
        # Example: Extract nouns as potential ingredients
        ingredients = [token.text for token in doc if token.pos_ == 'NOUN']
        # Assuming the last noun might be the ingredient for simplicity
        return ingredients[-1] if ingredients else None

    def recommend_recipes(self, ingredient: Text) -> List[Tuple[Text, Text]]:
        # Word2Vec similarity check
        if ingredient in model.wv.key_to_index:
            similar_ingredients = [i[0] for i in model.wv.most_similar(ingredient, topn=10)]
            # Get recipes and instructions containing similar ingredients
            recipes_subframe = data[data['TranslatedIngredients'].str.contains('|'.join(similar_ingredients), na=False, case=False)]
            recipes_subframe = recipes_subframe[['RecipeName', 'TranslatedInstructions']].head(5)
            # Convert DataFrame to list of tuples
            recommended_recipes = list(recipes_subframe.itertuples(index=False, name=None))
            return recommended_recipes
        else:
            return []
