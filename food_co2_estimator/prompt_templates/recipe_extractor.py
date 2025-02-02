from langchain.prompts import (
    AIMessagePromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)

from food_co2_estimator.output_parsers.recipe_extractor import Recipe

WEBSITE_RESPONSE_OBJ = Recipe(
    ingredients=[
        "500 gram torskefilet",
        "1 tsk havsalt",
        "2 stk æg",
        "1 stk gulerod, fintrevet",
        "0.5 dl fløde (13%)",
        "0.5 tsk revet muskatnød",
        "1 tsk peber",
        "2 spsk olie",
        "4 dl creme fraiche (18%)",
        "4 stk æggeblomme",
        "2 spsk frisk dild, hakket",
        "4 spsk frisk persille, hakket",
    ],
    persons=4,
    instructions=(
        "Forvarm ovnen til 180 grader Celsius. Skær torskefileten i mindre stykker og blend den "
        "sammen med havsalt i en foodprocessor til en fin konsistens. Tilsæt æg, fintrevet gulerod, "
        "fløde, revet muskatnød og peber. Blend igen, indtil massen er jævn. Smør en lille brødform "
        "eller ildfast fad med olie og hæld fiskefarsen i formen. Bag terrinen i ovnen i cirka 25-30 "
        "minutter, eller indtil den er fast og gylden på toppen. I mellemtiden piskes creme fraiche "
        "sammen med æggeblommer, hakket dild og persille. Opvarm saucen forsigtigt i en gryde over lav "
        "varme uden at koge den. Tag fisketerrinen ud af ovnen, lad den køle lidt af, og skær den i "
        "skiver. Server med den cremede sauce."
    ),
)
WEBSITE_RESPONSE = WEBSITE_RESPONSE_OBJ.model_dump_json()

RAW_TEXT_RESPONSE_OBJ = Recipe(
    ingredients=[
        "1 tomat",
        "2 løg",
        "200 g laks",
        "0.5 l mælk",
        "200 g kartofler",
    ],
    persons=2,
    instructions=None,
)
RAW_TEXT_RESPONSE = RAW_TEXT_RESPONSE_OBJ.model_dump_json()

NO_RECIPE_RESPONSE_OBJ = Recipe(
    ingredients=[],
    persons=None,
    instructions=None,
)
NO_RECIPE_RESPONSE = NO_RECIPE_RESPONSE_OBJ.model_dump_json()

example_input_1 = """
dansk hovedret 12 tilberedningstid 45 minutter arbejdstid 25 minutter print bedøm denne opskrift rated 4
/ 5 based on 1 customer reviews hov! du skal være logget ind. log ind bliv medlem ingredienser (12) 1 2 3 4 5 6 7 8
antal personer: 500 gram torskefilet 1 tsk havsalt 2 stk æg 1 stk gulerod 0.5 deciliter fløde 13% 0.5 tsk revet
muskatnød 1 tsk peber 2 spsk olie 4 deciliter creme fraiche 18% 4 stk æggeblomme 2 spsk frisk dild 4 spsk frisk persille
Forbered fiskefarsen ved at skære torskefileten i mindre stykker og blend den sammen med havsalt i en foodprocessor til en fin konsistens. Tilsæt de to hele æg, fintrevet gulerod, fløde, muskatnød og peber. Blend igen, indtil ingredienserne er godt blandet og konsistensen er jævn. Smag til med salt og peber efter behov
Forvarm ovnen til 180 grader. Smør en lille brødform eller ildfast fad med lidt olie og hæld fiskefarsen i formen. Glat overfladen ud. Bag terrinen i ovnen i cirka 25-30 minutter, eller indtil den er fast og let gylden på toppen
I en lille skål piskes creme fraiche sammen med æggeblommerne, hakket dild og persille. Smag til med salt og peber. Opvarm forsigtigt saucen i en lille gryde over lav varme, indtil den er varm, men undgå at koge den for at undgå at æggeblommerne skiller
Tag fisketerrinen ud af ovnen og lad den køle af i formen i et par minutter. Skær terrinen i skiver og anret på tallerkener. Hæld den cremede sauce over eller server den ved siden af
"""

example_input_2 = """
1 tomat2 løg200 g laks0.5 l mælk200 g kartofler
"""

example_input_3 = """
Det er dejligt vejr i dag. Jeg tror jeg vil gå en tur.
"""

system_prompt = """
Act as an expert in extracting recipes from text that understand Danish and English.
Given an unstructured raw text containing a recipe, extract the amount of each ingredient, the number of persons, and the instructions.
The instructions are the description of how you prepare the meal. 

Sometimes, there is no recipe to be found, and then you return an empty ingredients list and null in persons and instructions fields.

Sometimes the ingredients list is already provided. In that case, just output the input in the format described below, give an estimate of the number of persons, and provide a null as the instruction response.

Example of ingredients already provided in Danish: 
oksemørbrad (250 g)
2 gulerødder
Example of ingredients already provided in English:
250 g cream
400 g beef tenderloin

It is very important that you extract the number of persons (antal personer) from the text. If not able, then estimate the number of persons from the ingredient list based on the amounts in the ingredients.
If the instructions are avaiable, then it is important that you also extract the instructions!
If number of persons are not explicitly mentioned in text, then estimate from the amount of ingredients. 

The input/text is delimited by ####.

Begin!
"""

messages = [
    SystemMessagePromptTemplate.from_template(system_prompt),
    HumanMessagePromptTemplate.from_template("####{example_input_1}####"),
    AIMessagePromptTemplate.from_template("{website_response}"),
    HumanMessagePromptTemplate.from_template("####{example_input_2}####"),
    AIMessagePromptTemplate.from_template("{raw_text_response}"),
    HumanMessagePromptTemplate.from_template("####{example_input_3}####"),
    AIMessagePromptTemplate.from_template("{no_recipe_response}"),
    HumanMessagePromptTemplate.from_template("####{input}####"),
]

RECIPE_EXTRACTOR_PROMPT = ChatPromptTemplate(
    messages=messages,
    input_variables=["input"],
    partial_variables={
        "example_input_1": example_input_1,
        "website_response": WEBSITE_RESPONSE,
        "example_input_2": example_input_2,
        "raw_text_response": RAW_TEXT_RESPONSE,
        "example_input_3": example_input_3,
        "no_recipe_response": NO_RECIPE_RESPONSE,
    },
)
