EN_WEIGHT_EST_PROMPT = """
Given a list of ingredients, estimate the weights in kilogram for each ingredient.

The following recalculations can be used to estimate the weight of each ingredient:
1 can = 400 g
1 cube of bouillon/stock = 4 g
1 large onion = 285 g
1 medium onion = 170 g
1 small onion = 115 g
1 pepper = 150 g
1 tin of tomato concentrate = 140 g
1 tbsp. = 15 g
1 tsp. = 5 g
1 potato = 170 - 300 g
1 carrot = 100 g
1 lemon = 60 g

Use the following format:
Ingredients: "Ingredients here"
Answer: "Final answer here"

Begin!

Ingredients:
1 can of chopped tomatoes
2 large potatoes
3 teaspoons of sugar
200 g of pasta
500 ml of water
250 gram of minced meat
0.5 cauliflower
1 organic lemon
salt
pepper

Answer:
1 can of chopped tomatoes: 0.4 kg
2 large potatoes: 0.6 kg
3 teaspoons of sugar: 0.15 kg
200 g of pasta: 0.2 kg
500 ml of water: 0.5 kg
250 gram of minced meat: 0.25 kg
0.5 cauliflower: 0.250 kg (estimated by LLM model)
1 organic lemon: 0.06 kg
salt: negligible
pepper: negligible


Ingredients:
{input}
"""
