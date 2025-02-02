from langchain.chains.llm import LLMChain

from food_co2_estimator.language.detector import Languages
from food_co2_estimator.prompt_templates.weight_estimator import (
    DK_WEIGHT_EST_PROMPT,
    EN_WEIGHT_EST_PROMPT,
)
from food_co2_estimator.utils.openai_model import get_model


def get_weight_estimator_chain(language: Languages, verbose: bool = False):

    en_weight_est_chain = LLMChain(
        llm=get_model(),
        prompt=(
            EN_WEIGHT_EST_PROMPT
            if language == Languages.English
            else DK_WEIGHT_EST_PROMPT
        ),
        verbose=verbose,
    )

    return en_weight_est_chain
