from __future__ import annotations

import argparse
import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode


DEFAULT_MODEL = "llama-3.3-70b-versatile"
DEFAULT_THREAD_ID = "weather-demo"


@tool
def get_weather(query: str) -> str:
    """Return a simple weather report for the city mentioned in the query."""
    city = query.lower()

    if "delhi" in city:
        return "The temperature in Delhi is 45 degrees and sunny."
    if "indore" in city:
        return "The temperature in Indore is 25 degrees and cloudy."
    if "bengaluru" in city or "bangalore" in city:
        return "The temperature in Bengaluru is 25 degrees and cloudy."

    return "The temperature is 25 degrees and cloudy."


def load_llm(model_name: str = DEFAULT_MODEL) -> ChatGroq:
    load_dotenv()

    if not os.getenv("GROQ_API_KEY"):
        raise RuntimeError("Set GROQ_API_KEY in your environment or .env file.")

    return ChatGroq(model_name=model_name)


def build_agent(model_name: str = DEFAULT_MODEL) -> Any:
    tools = [get_weather]
    llm = load_llm(model_name).bind_tools(tools)
    tool_node = ToolNode(tools)
    memory = MemorySaver()

    def call_model(state: MessagesState) -> dict[str, list[BaseMessage]]:
        response = llm.invoke(state["messages"])
        return {"messages": [response]}

    def route_next(state: MessagesState) -> str:
        last_message = state["messages"][-1]

        if getattr(last_message, "tool_calls", None):
            return "tools"

        return END

    graph = StateGraph(MessagesState)
    graph.add_node("agent", call_model)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "agent")
    graph.add_conditional_edges(
        "agent",
        route_next,
        {
            "tools": "tools",
            END: END,
        },
    )
    graph.add_edge("tools", "agent")

    return graph.compile(checkpointer=memory)


def ask_agent(app: Any, question: str, thread_id: str = DEFAULT_THREAD_ID) -> str:
    config = {"configurable": {"thread_id": thread_id}}
    state = app.invoke(
        {"messages": [HumanMessage(content=question)]},
        config=config,
    )

    return state["messages"][-1].content


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the LangGraph weather agent.")
    parser.add_argument(
        "question",
        nargs="*",
        default=["what", "is", "the", "weather", "in", "delhi?"],
    )
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--thread-id", default=DEFAULT_THREAD_ID)
    args = parser.parse_args()

    question = " ".join(args.question)
    app = build_agent(model_name=args.model)
    answer = ask_agent(app, question, thread_id=args.thread_id)
    print(answer)


if __name__ == "__main__":
    main()
