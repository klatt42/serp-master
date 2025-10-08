from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import SystemMessage, HumanMessage
from tools.dataforseo_tools import get_keyword_data, get_serp_data, get_competitor_data
import os

def create_seo_agent():
    """Create the SEO assistant agent using LangGraph."""

    # Initialize the LLM
    llm = ChatOpenAI(
        model="gpt-4",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Define the tools the agent can use
    tools = [
        get_keyword_data,
        get_serp_data,
        get_competitor_data,
    ]

    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(tools)

    # System message for the agent
    system_message = SystemMessage(
        content="""You are SERP Master, an expert SEO assistant powered by AI.

Your capabilities include:
- Keyword research and analysis
- SERP (Search Engine Results Page) analysis
- Competitor intelligence and tracking
- SEO strategy recommendations
- Content optimization suggestions

You have access to real-time SEO data through DataForSEO APIs. When users ask about:
- Keywords: Use get_keyword_data to fetch search volume, competition, and trends
- SERP analysis: Use get_serp_data to analyze search results for specific queries
- Competitors: Use get_competitor_data to research competitor strategies

Be conversational, helpful, and provide actionable insights. Always explain technical SEO concepts in an accessible way.
When providing data, format it clearly and highlight the most important insights."""
    )

    def call_model(state: MessagesState):
        """Call the LLM with the current state."""
        messages = [system_message] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}

    # Build the graph
    builder = StateGraph(MessagesState)

    # Add nodes
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))

    # Add edges
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        tools_condition,
    )
    builder.add_edge("tools", "call_model")

    # Compile the graph
    graph = builder.compile()

    return graph
