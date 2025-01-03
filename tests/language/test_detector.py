import pytest

from food_co2_estimator.language.detector import Languages, detect_language
from food_co2_estimator.pydantic_models.recipe_extractor import (
    EnrichedIngredient,
    EnrichedRecipe,
)


def _create_enriched_recipe(
    ingredients: list[str], instructions: str | None, persons: int | None = 2
) -> EnrichedRecipe:
    return EnrichedRecipe(
        url="http://example.com",
        ingredients=[EnrichedIngredient(original_name=ing) for ing in ingredients],
        instructions=instructions,
        persons=persons,
    )


def test_english_instructions():
    recipe = _create_enriched_recipe(
        ingredients=["eggplant", "cucumber"],
        instructions="Preheat the oven to 180 degrees. Add salt and pepper.",
    )
    assert detect_language(recipe) == Languages.English


def test_danish_instructions():
    recipe = _create_enriched_recipe(
        ingredients=["aubergine", "agurk"],
        instructions="Forvarm ovnen til 180 grader. Tilsæt salt og peber.",
    )
    assert detect_language(recipe) == Languages.Danish


@pytest.mark.parametrize(
    "instructions,expected",
    [
        (
            "Forvarm ovnen til 180 grader. Dette er en norsk oppskrift.",
            Languages.Danish,
        ),
        (
            "Förvärm ugnen till 180 grader. Detta är ett svenskt recept.",
            Languages.Danish,
        ),
    ],
)
def test_scandinavian_languages_as_danish(instructions, expected):
    recipe = _create_enriched_recipe(
        ingredients=["salt", "pepper"],
        instructions=instructions,
    )
    assert detect_language(recipe) == expected


@pytest.mark.parametrize(
    "ingredients,expected",
    [
        (
            ["500 gram torsk", "1 tsk fløde"],
            Languages.Danish,
        ),
        (
            ["500 grams salmon", "1 tsp cream"],
            Languages.English,
        ),
    ],
)
def test_language_from_ingredients_no_instructions(ingredients, expected):
    recipe = _create_enriched_recipe(
        ingredients=ingredients,
        instructions=None,
    )
    assert detect_language(recipe) == expected


def test_empty_recipe_raises_exception():
    recipe = _create_enriched_recipe(
        ingredients=[],
        instructions=None,
        persons=None,
    )
    with pytest.raises(Exception):
        detect_language(recipe)


def test_single_word_ingredients():
    recipe = _create_enriched_recipe(
        ingredients=["agurk", "gulerod", "ærter"],
        instructions=None,
    )
    assert detect_language(recipe) == Languages.Danish
