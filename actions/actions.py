
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from typing import Any, Text, Dict, List, Tuple
import pandas as pd
import numpy as np
import joblib
from sklearn.metrics.pairwise import cosine_similarity
import nltk
import re
import spacy
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import logging
from spellchecker import SpellChecker

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('stopwords')


class ActionRecommendRecipe(Action):
    def name(self) -> Text:
        return "action_recommend_recipe"
    

    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_md")  # Ensure this matches the spaCy model used for TF-IDF
        self.data = pd.read_csv('/home/kaushalpancholi/Desktop/NLP-Project/RecipeRover/data/IndianFoodDatasetCSV.csv')
        self.tfidf_vectorizer = joblib.load('/home/kaushalpancholi/Desktop/NLP-Project/tfidf_vectorizer1.joblib')
        self.tfidf_matrix = joblib.load('/home/kaushalpancholi/Desktop/NLP-Project/tfidf_matrix1.joblib')
        self.stop_words = set(stopwords.words('english'))
        self.spell = SpellChecker()
        self.custom_dict = {'paneer', 'milk', 'ghee', 'masala', 'curry', 'chai', 'korma','karela','pavakkai', 'aloo','puri', 'eggs', 'egg'}
    
    def preprocess_text(self, text):
        text = text.lower()
        text = re.sub(r'\d+', '', text)  
        text = re.sub(r'<.*?>', '', text)  
        
        text = re.sub(r'[^\w\s]', '', text)  
        # Tokenize the text
        words = text.split()
        # Correct spelling with check against custom dictionary
        corrected_words = [word if word in self.custom_dict else self.spell.correction(word) for word in words]
        # Join the corrected words back into a string
        corrected_text = ' '.join(corrected_words)
        common_words = {'recipe', 'recipes', 'want', 'make', 'something', 'cook', 'and', 'a', 'a recipe','any recipes','table','spoon', 'tablespoon','utensils', 'subbu','sub','glass','glasses','cup','cups','teaspoon','pinch','area','noodles','manchurian','Manchurian', 'suburb'} 
        doc = self.nlp(corrected_text)
        all_stops = self.stop_words.union(common_words)
        ingredients = ' '.join([chunk.text for chunk in doc.noun_chunks if chunk.text not in all_stops])        
        return ingredients

    def extract_ingredient(self, text: Text) -> Text:
        return self.preprocess_text(text)

    def recommend_recipes(self, input_ingredient: Text) -> List[Tuple[Text, Text, Text]]:
        logger.info(f"Input ingredient: {input_ingredient}")
        input_vec = self.tfidf_vectorizer.transform([input_ingredient])
        logger.debug(f"Input vector shape: {input_vec.shape}")
        cosine_similarities = cosine_similarity(input_vec, self.tfidf_matrix).flatten()
        logger.debug(f"Cosine similarities: {cosine_similarities}")
        top_indices = cosine_similarities.argsort()[-3:][::-1]
        logger.debug(f"Top indices: {top_indices}")
        recommended_recipes = self.data.iloc[top_indices]
        logger.info(f"Recommended recipes: {recommended_recipes[['RecipeName']].values.tolist()}")        
        return [(row['RecipeName'], row['TranslatedIngredients'], row['TranslatedInstructions']) for index, row in recommended_recipes.iterrows()]

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        ingredient = self.extract_ingredient(tracker.latest_message.get('text', ''))
        if ingredient:
            recommended_recipes = self.recommend_recipes(ingredient)
            if recommended_recipes:
                # First, send all the recipe data
                for recipe in recommended_recipes:
                    dispatcher.utter_message(text=f"Recipe: {recipe[0]}")
                    dispatcher.utter_message(text=f"Ingredients: {recipe[1]}")
                    dispatcher.utter_message(text=f"Instructions: {recipe[2]}")

                # After all recipes are sent, ask if the user wants more
                dispatcher.utter_message(text="Would you like to look for more recipes?")
            else:
                # If no recipes are found, inform the user
                dispatcher.utter_message(text="I couldn't find any recipes with that ingredient.")
                # Ask if the user wants to search again
                dispatcher.utter_message(text="Would you like to look for more recipes?")
        else:
            # If no ingredient is provided, prompt the user for one
            dispatcher.utter_message(text="I don't recognize that ingredient. Can you try another one?")

        return []



    

    

