import json
from typing import List

from food_co2_estimator.language.detector import Languages
from food_co2_estimator.output_parsers.co2_estimator import CO2Emissions
from food_co2_estimator.output_parsers.search_co2_estimator import CO2SearchResult
from food_co2_estimator.output_parsers.weight_estimator import WeightEstimates

# Avg. dinner emission per person method:
# 1. Get Food emission per person per year here: https://concito.dk/udgivelser/danmarks-globale-forbrugsudledninger which is 1.97 ton / per capita
# 2. Estimate emission per day per capita: 1.97 / 365.25 * 1000 = 5.39 kg CO2 / per capita
# 3. Calculate ratio of dinenr calorie amount wrt. to daily calorie intake:
#     Minimum case; 600 calories / 2500 calories = 0.24. Maximum case: 0.4. Avg. case = 700 / 2250 = 0.31
# 4. Assume dinner emission is equivalent to amount of calories to estimate avg. dinner emission.
#    5.39 * 0.24 = 1.69 kg CO2 per capita

MIN_DINNER_EMISSION_PER_CAPITA = 1.3
MAX_DINNER_EMISSION_PER_CAPITA = 2.2

def generate_output(
    weight_estimates: WeightEstimates,
    co2_emissions: CO2Emissions,
    search_results: List[CO2SearchResult],
    negligeble_threshold: float,
    number_of_persons: int | None,
    language: Languages = Languages.English,
    recipe_url: str = ""  # Add the URL as an input if you have it available
) -> str:
    translations = {
        Languages.English: {
            "unable": "unable to estimate weight",
            "negligible": "weight on {} kg is negligible",
            "not_found": "CO2e per kg not found",
            "total": "Total CO2 emission",
            "persons": "Estimated number of persons",
            "emission_pr_person": "Emission pr. person",
            "avg_meal_emission_pr_person": "Avg. Danish dinner emission pr person",
            "method": "The calculation method per ingredient is",
            "legends": "Legends",
            "db": "(DB) - Data from SQL Database (https://denstoreklimadatabase.dk)",
            "search": "(Search) - Data obtained from search",
            "comments": "Comments",
            "for": "For",
        },
        Languages.Danish: {
            "unable": "kan ikke skønne vægt",
            "negligible": "vægt på {} kg er negligerbar",
            "not_found": "CO2e per kg ikke fundet",
            "total": "Samlet CO2-udslip",
            "persons": "Estimeret antal personer",
            "emission_pr_person": "Emission pr. person",
            "avg_meal_emission_pr_person": "Gennemsnitligt aftensmad udledning pr. person",
            "method": "Beregningsmetoden pr. ingrediens er",
            "legends": "Forklaring",
            "db": "(DB) - Data fra SQL Database (https://denstoreklimadatabase.dk)",
            "search": "(Søgning) - Data opnået fra søgning",
            "comments": "Kommentarer",
            "for": "For",
        },
    }

    trans = translations.get(language, translations[Languages.English])

    ingredient_data = []
    total_co2 = 0
    all_comments = []

    for weight_estimate in weight_estimates.weight_estimates:
        co2_data = next(
            (
                item
                for item in co2_emissions.emissions
                if item.ingredient == weight_estimate.ingredient
            ),
            None,
        )
        search_result = next(
            (
                item
                for item in search_results
                if item.ingredient == weight_estimate.ingredient
            ),
            None,
        )

        comments = {
            "Weight": weight_estimate.weight_calculation,
            "DB": co2_data.comment if co2_data else None,
            "Search": search_result.explanation if search_result else None,
        }

        all_comments.append(
            {"ingredient": weight_estimate.ingredient, "comments": comments}
        )

        if weight_estimate.weight_in_kg is None:
            ingredient_data.append({
                "name": weight_estimate.ingredient,
                "weight_kg": None,
                "co2_kg": None,
                "status": trans['unable'],
                "method": None
            })
            continue

        if weight_estimate.weight_in_kg <= negligeble_threshold:
            ingredient_data.append({
                "name": weight_estimate.ingredient,
                "weight_kg": weight_estimate.weight_in_kg,
                "co2_kg": 0,
                "status": trans['negligible'].format(round(weight_estimate.weight_in_kg,3)),
                "method": None
            })
            continue

        if co2_data and co2_data.co2_per_kg:
            co2_value = round(co2_data.co2_per_kg * weight_estimate.weight_in_kg, 2)
            total_co2 += co2_value
            ingredient_data.append({
                "name": weight_estimate.ingredient,
                "weight_kg": round(weight_estimate.weight_in_kg, 2),
                "co2_kg": co2_value,
                "status": "OK",
                "method": "DB"
            })
        elif search_result and search_result.result:
            co2_value = round(search_result.result * weight_estimate.weight_in_kg, 2)
            total_co2 += co2_value
            ingredient_data.append({
                "name": weight_estimate.ingredient,
                "weight_kg": round(weight_estimate.weight_in_kg, 2),
                "co2_kg": co2_value,
                "status": "OK",
                "method": "Search"
            })
        else:
            ingredient_data.append({
                "name": weight_estimate.ingredient,
                "weight_kg": round(weight_estimate.weight_in_kg, 2),
                "co2_kg": None,
                "status": trans['not_found'],
                "method": None
            })

    if number_of_persons is not None and number_of_persons > 0:
        co2_per_person = round(total_co2 / number_of_persons, 1)
    else:
        co2_per_person = None

    result_dict = {
        "recipe_url": recipe_url,
        "total_co2_kg": round(total_co2, 1),
        "number_of_persons": number_of_persons,
        "co2_per_person_kg": co2_per_person,
        "avg_meal_emission_per_person_range_kg": [MIN_DINNER_EMISSION_PER_CAPITA, MAX_DINNER_EMISSION_PER_CAPITA],
        "ingredients": ingredient_data,
        "comments": all_comments
    }

    # Convert dict to JSON string
    json_output = json.dumps(result_dict, ensure_ascii=False, indent=2)
    print(json_output)
    return json_output
