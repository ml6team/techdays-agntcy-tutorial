# Copyright AGNTCY Contributors (https://github.com/agntcy)
# SPDX-License-Identifier: Apache-2.0

import logging
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END
from common.llm import get_llm
from ioa_observe.sdk.decorators import agent, graph
from agntcy_app_sdk.factory import AgntcyFactory
from config.config import DEFAULT_MESSAGE_TRANSPORT, TRANSPORT_SERVER_ENDPOINT
from langchain_core.messages import AIMessage


logger = logging.getLogger("lungo.vietnam_farm_agent.agent")

# --- 1. Define Node Names as Constants ---
class NodeStates:
    SUPERVISOR = "supervisor"
    INVENTORY = "inventory_node"
    ORDERS = "orders_node"
    GENERAL_RESPONSE = "general_response_node"
    MONSOON_CHECK = "monsoon_check_node"


# --- 2. Define the Graph State ---
class GraphState(MessagesState):
    """
    Represents the state of our graph, passed between nodes.
    """
    next_node: str
    monsoon_status: str | None

# --- 3. Implement the LangGraph Application Class ---
@agent(name="vietnam_farm_agent")
class FarmAgent:
    def __init__(self):
        """
        Initializes the CustomerServiceAgent with an LLM and builds the LangGraph workflow.

        Args:
            llm_model (str): The name of the OpenAI LLM model to use (e.g., "gpt-4o", "gpt-3.5-turbo").
        """
        self.supervisor_llm = None
        self.inventory_llm = None
        self.orders_llm = None

        self.app = self._build_graph()

    # --- Node Definitions ---

    def _supervisor_node(self, state: GraphState) -> dict:
        """
        Determines the intent of the user's message and routes to the appropriate node.
        """
        if not self.supervisor_llm:
            self.supervisor_llm = get_llm()

        prompt = PromptTemplate(
            template="""You are a coffee farm manager in Vietnam who delegates farm cultivation and global sales. Based on the 
            user's message, determine if it's related to 'inventory' or 'orders'.
            Respond with 'inventory' if the message is about checking yield, stock, product availability, or specific coffee item details.
            Respond with 'orders' if the message is about checking order status, placing an order, or modifying an existing order.
            If unsure, respond with 'general'.

            User message: {user_message}
            """,
            input_variables=["user_message"]
        )

        chain = prompt | self.supervisor_llm
        response = chain.invoke({"user_message": state["messages"]})
        intent = response.content.strip().lower()

        logger.info(f"Supervisor intent determined: {intent}")  # Log the intent for debugging

        if "inventory" in intent:
            return {"next_node": NodeStates.MONSOON_CHECK, "messages": state["messages"]}
        elif "orders" in intent:
            return {"next_node": NodeStates.ORDERS, "messages": state["messages"]}
        else:
            return {"next_node": NodeStates.GENERAL_RESPONSE, "messages": state["messages"]}

    def _inventory_node(self, state: GraphState) -> dict:
        """
        Handles inventory-related queries using an LLM to formulate responses.
        """
        if not self.inventory_llm:
            self.inventory_llm = get_llm()

        user_message = state["messages"]
        monsoon_status_line = state.get("monsoon_status") or "There are no monsoon updates."

        prompt = PromptTemplate(
            template="""You are a helpful coffee farm cultivation manager in Vietnam who handles yield or inventory requests.
            First output exactly this status line on its own line:
            {monsoon_status_line}

            Then on the next line output ONLY the numeric yield estimate with units.
            - If the user asked in lbs/pounds, use pounds. If they asked in kg/kilograms, convert to kg.
            - If the status line indicates monsoon conditions (exact text: "There are monsoon conditions."), reduce the estimate by 30% to reflect expected impact.
            - Do not add any extra wording beyond the two lines described.

            User question: {user_message}
            """,
            input_variables=["user_message", "monsoon_status_line"]
        )
        chain = prompt | self.inventory_llm

        llm_response = chain.invoke({
            "user_message": user_message,
            "monsoon_status_line": monsoon_status_line,
        }).content

        logger.info(f"Inventory response generated: {llm_response}")

        return {"messages": [AIMessage(llm_response)]}

    def _orders_node(self, state: GraphState) -> dict:
        """
        Handles order-related queries using an LLM to formulate responses.
        """
        if not self.orders_llm:
            self.orders_llm = get_llm()

        user_message = state["messages"]

        logger.info(f"Received order query: {user_message}")

        # Simulate data retrieval - in a real app, this would be a database/API call
        mock_order_data = {
            "12345": {"status": "processing", "estimated_delivery": "2 business days"},
            "67890": {"status": "shipped", "tracking_number": "ABCDEF123"}
        }

        prompt = PromptTemplate(
            template="""You are an order assistant. Based on the user's question and the following order data, provide a concise and helpful response.
            If they ask about a specific order number, provide its status. 
            If they ask about placing order an order, generate a random order id and tracking number.

            Order Data: {order_data}
            User question: {user_message}
            """,
            input_variables=["user_message", "order_data"]
        )
        chain = prompt | self.orders_llm

        llm_response = chain.invoke({
            "user_message": user_message,
            "order_data": str(mock_order_data) # Pass data as string for LLM context
        }).content

        return {"messages": [AIMessage(llm_response)]}

    def _general_response_node(self, state: GraphState) -> dict:
        """
        Provides a fallback response for unclear or out-of-scope messages.
        """
        response = "I'm designed to help with inventory and order-related questions. Could you please rephrase your request?"
        return {"messages": [AIMessage(response)]}

    # --- Graph Building Method ---
    @graph(name="vietnam_farm_graph")
    def _build_graph(self):
        """
        Builds and compiles the LangGraph workflow.
        """
        workflow = StateGraph(GraphState)

        # Add nodes
        workflow.add_node(NodeStates.SUPERVISOR, self._supervisor_node)
        workflow.add_node(NodeStates.INVENTORY, self._inventory_node)
        workflow.add_node(NodeStates.ORDERS, self._orders_node)
        workflow.add_node(NodeStates.GENERAL_RESPONSE, self._general_response_node)
        workflow.add_node(NodeStates.MONSOON_CHECK, self._monsoon_check_node)


        # Set the entry point
        workflow.set_entry_point(NodeStates.SUPERVISOR)

        # Add conditional edges from the supervisor
        workflow.add_conditional_edges(
            NodeStates.SUPERVISOR,
            lambda state: state["next_node"],
            {
                NodeStates.MONSOON_CHECK: NodeStates.MONSOON_CHECK,
                NodeStates.INVENTORY: NodeStates.INVENTORY,
                NodeStates.ORDERS: NodeStates.ORDERS,
                NodeStates.GENERAL_RESPONSE: NodeStates.GENERAL_RESPONSE,
            },
        )

        # Add edges from the specific nodes to END
        workflow.add_edge(NodeStates.MONSOON_CHECK, NodeStates.INVENTORY)
        workflow.add_edge(NodeStates.INVENTORY, END)
        workflow.add_edge(NodeStates.ORDERS, END)
        workflow.add_edge(NodeStates.GENERAL_RESPONSE, END)

        return workflow.compile()

    # --- Public Methods for Interaction ---

    async def ainvoke(self, user_message: str) -> dict:
        """
        Invokes the graph with a user message.

        Args:
            user_message (str): The current message from the user.

        Returns:
            str: The final state of the graph after processing the message.
        """
        inputs = {"messages": [user_message]}
        result = await self.app.ainvoke(inputs)

        messages = result.get("messages", [])
        if not messages:
            raise RuntimeError("No messages found in the graph response.")

        # Find the last AIMessage with non-empty content
        for message in reversed(messages):
            if isinstance(message, AIMessage) and message.content.strip():
                logger.debug(f"Valid AIMessage found: {message.content.strip()}")
                return message.content.strip()

        # If no valid AIMessage found, return the last message as a fallback
        return messages[-1].content.strip() if messages else "No valid response generated."

    async def _monsoon_check_node(self, state: GraphState) -> dict:
        """
        Calls the MCP server to check for monsoon conditions in Vietnam.
        """
        # Initialize AGNTCY factory
        factory = AgntcyFactory("lungo_vietnam_farm", enable_tracing=True)

        # Create transport for MCP communication
        transport_instance = factory.create_transport(
            DEFAULT_MESSAGE_TRANSPORT,
            endpoint=TRANSPORT_SERVER_ENDPOINT,
            name="default/default/mcp_client"
        )

        # Create MCP client connected to the weather server
        mcp_client = factory.create_client(
            "MCP",
            agent_topic="lungo_weather_service",  # MCP server topic
            transport=transport_instance,
        )

        try:
            async with mcp_client as client:
                logger.info("MCP monsoon check: calling get_monsoon_status for 'Vietnam Highlands'")
                # Call the MCP tool for monsoon status
                result = await client.call_tool(
                    name="get_monsoon_status",
                    arguments={"location": "Vietnam Highlands"},
                )

                # Handle streamed or normal response
                monsoon_message = ""
                if hasattr(result, "__aiter__"):  # streaming response
                    async for chunk in result:
                        delta = chunk.choices[0].delta
                        monsoon_message += delta.content or ""
                else:
                    content_list = getattr(result, "content", [])
                    if isinstance(content_list, list) and len(content_list) > 0:
                        monsoon_message = content_list
0                # Derive concise status line for downstream prompt
wind_speed} m/s")
                else:
                    logger.info("Wind speed not found in MCP response.")

# Derive concise status line for downstream prompt                status_line: str | None = None
                lower = (monsoon_message or "").lower()
                if ("monsoon" in lower) and ("detected" in lower or "🌧️" in lower):
                    status_line = "There are monsoon conditions."

                return {"messages": [AIMessage(monsoon_message)], "monsoon_status": status_line}

        except Exception as e:
            logger.error(f"MCP monsoon check error: {e}")
            return {"messages": [AIMessage(f"Error retrieving monsoon data: {str(e)}")]}
