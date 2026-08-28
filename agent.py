import json
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types  # pyright: ignore[reportMissingImports]

from tools import (
    search_customers,
    get_deals_for_customer,
    search_deals,
    count_leads_by_status,
    get_customer_history,
    get_at_risk_deals
)


load_dotenv()


GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)


if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY is missing. "
        "Add it to your .env file."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


SYSTEM_INSTRUCTION = """
You are an AI-powered CRM Assistant.

Your job is to help sales and support teams
understand and manage CRM information.

CRM DATA RULES:

1. Never invent customers.

2. Never invent deals.

3. Never invent notes.

4. Never invent interactions.

5. All factual CRM answers must be based
   on tool results.

6. If a customer cannot be found, clearly
   say that the customer does not exist
   in the CRM.

7. If multiple customers match a name,
   ask the user to specify the company
   or customer ID.

8. Do not guess which customer or deal
   the user means.

9. Read-only requests can use CRM tools.

10. CRM write actions require confirmation.
    Do NOT directly execute write operations.

11. If the user asks to update a deal,
    add a note or assign a lead, identify
    the exact customer/deal first.

12. Never claim an action was completed
    unless the application confirms it.

13. Keep answers concise and professional.

14. Currency should be displayed in dollars.

15. You can suggest next actions based
    only on available CRM information.
"""


# =========================================================
# GEMINI FUNCTION DECLARATIONS
# =========================================================

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="search_customers",
                description=(
                    "Search customers by name, "
                    "company, email or customer ID."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "query": types.Schema(
                            type="STRING",
                            description=(
                                "Customer name, "
                                "company, email or ID."
                            )
                        )
                    },
                    required=["query"]
                )
            ),

            types.FunctionDeclaration(
                name="get_deals_for_customer",
                description=(
                    "Get all deals belonging to "
                    "an exact customer ID."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "customer_id": types.Schema(
                            type="STRING",
                            description=(
                                "Exact customer ID."
                            )
                        )
                    },
                    required=["customer_id"]
                )
            ),

            types.FunctionDeclaration(
                name="search_deals",
                description=(
                    "Search CRM deals using "
                    "minimum value, inactivity "
                    "days and optional status."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "min_value": types.Schema(
                            type="NUMBER",
                            description=(
                                "Minimum deal value."
                            )
                        ),
                        "inactive_days": types.Schema(
                            type="INTEGER",
                            description=(
                                "Deals not updated "
                                "for this many days."
                            )
                        ),
                        "status": types.Schema(
                            type="STRING",
                            description=(
                                "Optional status."
                            )
                        )
                    }
                )
            ),

            types.FunctionDeclaration(
                name="count_leads_by_status",
                description=(
                    "Count leads/deals with "
                    "a specific CRM status."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "status": types.Schema(
                            type="STRING",
                            description=(
                                "New, Contacted, "
                                "Won or Lost."
                            )
                        )
                    },
                    required=["status"]
                )
            ),

            types.FunctionDeclaration(
                name="get_customer_history",
                description=(
                    "Get the customer's deals, "
                    "notes and interactions."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "customer_id": types.Schema(
                            type="STRING",
                            description=(
                                "Exact customer ID."
                            )
                        )
                    },
                    required=["customer_id"]
                )
            ),

            types.FunctionDeclaration(
                name="get_at_risk_deals",
                description=(
                    "Find high-value deals that "
                    "have not been updated recently "
                    "and are still open."
                ),
                parameters=types.Schema(
                    type="OBJECT",
                    properties={
                        "inactive_days": types.Schema(
                            type="INTEGER"
                        ),
                        "min_value": types.Schema(
                            type="NUMBER"
                        )
                    }
                )
            )
        ]
    )
]


# =========================================================
# READ TOOL EXECUTION
# =========================================================

def execute_tool(
    function_name,
    arguments
):

    if function_name == "search_customers":

        return search_customers(
            arguments["query"]
        )


    if function_name == "get_deals_for_customer":

        return get_deals_for_customer(
            arguments["customer_id"]
        )


    if function_name == "search_deals":

        return search_deals(
            min_value=arguments.get(
                "min_value",
                0
            ),
            inactive_days=arguments.get(
                "inactive_days",
                0
            ),
            status=arguments.get(
                "status"
            )
        )


    if function_name == "count_leads_by_status":

        return count_leads_by_status(
            arguments["status"]
        )


    if function_name == "get_customer_history":

        return get_customer_history(
            arguments["customer_id"]
        )


    if function_name == "get_at_risk_deals":

        return get_at_risk_deals(
            inactive_days=arguments.get(
                "inactive_days",
                14
            ),
            min_value=arguments.get(
                "min_value",
                10000
            )
        )


    return {
        "error": (
            f"Unknown tool: {function_name}"
        )
    }


# =========================================================
# AGENT
# =========================================================

def run_agent(user_message: str):

    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=user_message
                )
            ]
        )
    ]

    for _ in range(5):

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                tools=TOOLS,
                temperature=0.1
            )
        )

        function_calls = []

        for part in response.candidates[0].content.parts:

            if part.function_call:
                function_calls.append(
                    part.function_call
                )

        # No more tool calls
        if not function_calls:

            return {
                "type": "answer",
                "response": response.text
            }

        # Add Gemini's tool-call message
        contents.append(
            response.candidates[0].content
        )

        # Execute requested tools
        tool_response_parts = []

        for function_call in function_calls:

            function_name = function_call.name

            arguments = dict(
                function_call.args
            )

            result = execute_tool(
                function_name,
                arguments
            )

            tool_response_parts.append(
                types.Part.from_function_response(
                    name=function_name,
                    response={
                        "result": result
                    }
                )
            )

        # Send tool result back to Gemini
        contents.append(
            types.Content(
                role="tool",
                parts=tool_response_parts
            )
        )

    return {
        "type": "answer",
        "response": "I couldn't complete the CRM request."
    }