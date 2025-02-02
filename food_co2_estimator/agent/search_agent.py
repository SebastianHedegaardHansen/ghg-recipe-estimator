from typing import Literal

from langchain.agents import AgentExecutor, Tool, ZeroShotAgent
from langchain.chains.llm import LLMChain
from langchain_community.utilities import GoogleSearchAPIWrapper, GoogleSerperAPIWrapper
from langchain_core.prompts import PromptTemplate

from food_co2_estimator.output_parsers.search_co2_estimator import (
    search_co2_output_parser,
)
from food_co2_estimator.prompt_templates.search_co2_estimator import (
    SEARCH_AGENT_FORMAT_INSTRUCTIONS,
    SEARCH_AGENT_PROMPT_PREFIX,
    SEARCH_AGENT_PROMPT_SUFFIX,
)
from food_co2_estimator.utils.openai_model import get_model


def get_co2_google_search_agent(
    verbose: bool = False, search_type: Literal["google", "serper"] = "serper"
):
    if search_type == "google":
        search_chain = GoogleSearchAPIWrapper(k=10, search_engine="google")
        coroutine = None
    else:
        search_chain = GoogleSerperAPIWrapper(k=10, gl="dk")
        coroutine = search_chain.arun

    tools = [
        Tool(
            name="Search",
            func=search_chain.run,
            description="""Useful for finding out the kg CO2e / kg for an ingredient. You are only allowed to use the tool once.""",
            coroutine=coroutine,
        ),
    ]

    # Hacky method to use zero shot agent. Properly is a better method
    tool_strings = "\n".join([f"{tool.name}: {tool.description}" for tool in tools])
    tool_names = ", ".join([tool.name for tool in tools])
    format_instructions = SEARCH_AGENT_FORMAT_INSTRUCTIONS.format(
        tool_names=tool_names,
    )
    format_instructions2 = "{format_instructions}"
    template = "\n\n".join(
        [
            SEARCH_AGENT_PROMPT_PREFIX,
            tool_strings,
            format_instructions,
            format_instructions2,
            SEARCH_AGENT_PROMPT_SUFFIX,
        ]
    )

    prompt = PromptTemplate(
        template=template,
        input_variables=["input", "agent_scratchpad"],
        output_parser=search_co2_output_parser,
        partial_variables={
            "format_instructions": search_co2_output_parser.get_format_instructions()
        },
    )

    llm_chain = LLMChain(
        llm=get_model(),  # type: ignore
        prompt=prompt,
    )

    tool_names = [tool.name for tool in tools]
    agent = ZeroShotAgent(llm_chain=llm_chain, allowed_tools=tool_names)
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=verbose
    )

    return agent_executor


if __name__ == "__main__":
    search = GoogleSearchAPIWrapper(k=20, search_engine="google")

    search.run("basilikum kg CO2e per kg")
