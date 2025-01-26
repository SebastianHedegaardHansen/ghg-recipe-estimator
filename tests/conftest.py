import pytest

from food_co2_estimator.pydantic_models.recipe_extractor import (
    EnrichedRecipe,
    ExtractedRecipe,
)
from tests.load_files import (
    get_expected_enriched_recipe,
    get_expected_extracted_recipe,
    get_expected_weight_estimates,
    get_recipe_markdown_text,
)
from tests.urls import TEST_URLS


@pytest.fixture
def dummy_recipe():
    return ExtractedRecipe(
        persons=2,
        ingredients=["ingredient1", "ingredient2"],
        instructions="instructions",
    )


@pytest.fixture(params=TEST_URLS.keys())
def markdown_and_expected_extracted_recipe_fixture(request: pytest.FixtureRequest):
    file_name = request.param
    markdown_text = get_recipe_markdown_text(file_name)

    expected_output = get_expected_extracted_recipe(file_name)
    return markdown_text, expected_output


@pytest.fixture(params=TEST_URLS.keys())
def enriched_recipe_fixture(request: pytest.FixtureRequest):
    file_name = request.param
    return file_name, get_expected_enriched_recipe(file_name)


def enriched_recipe_with_weight_est_fixture(
    enriched_recipe_fixture: tuple[str, EnrichedRecipe],
) -> tuple[str, EnrichedRecipe]:
    file_name, enriched_recipe = enriched_recipe_fixture
    weight_estimates = get_expected_weight_estimates(file_name)
    enriched_recipe.update_with_weight_estimates(weight_estimates)
    return file_name, enriched_recipe
