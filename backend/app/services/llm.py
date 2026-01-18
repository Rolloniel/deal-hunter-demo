"""OpenAI LLM service with tool calling for intent extraction."""

import json
from typing import Any
from openai import AsyncOpenAI
from app.config import get_settings

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)

# System prompt with guardrails
SYSTEM_PROMPT = """You are DealHunter, a product deal tracking assistant.

RULES:
- You help users track product prices and get recommendations.
- You do NOT track flights or travel - politely redirect to product deals.
- You NEVER hallucinate prices - use tools to get real data.
- You are concise - max 2-3 sentences per response.
- If you can't understand the request, ask for clarification.

When user wants to track something, extract:
- Product name (as specific as possible)
- Target price (if mentioned, otherwise ask)

Available actions:
- Track a product at a target price
- Get product recommendations by category
- List currently tracked items"""

# Tool definitions for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "track_product",
            "description": "Add a product to the user's watchlist with a target price. Call this when user wants to track a product price.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to track (e.g., 'Samsung 65 inch TV', 'Sony WH-1000XM5 Headphones')",
                    },
                    "target_price": {
                        "type": "number",
                        "description": "The target price in USD. Alert when price drops below this.",
                    },
                },
                "required": ["product_name", "target_price"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_recommendations",
            "description": "Get product recommendations by category and max price. Call this when user asks for deals or recommendations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Product category (e.g., 'TV', 'Headphones', 'Laptop', 'Electronics')",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in USD for recommendations",
                    },
                },
                "required": ["category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tracked_items",
            "description": "List all products the user is currently tracking. Call this when user asks what they're tracking.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
]


async def process_message(
    message: str, session_id: str, conversation_history: list[dict] | None = None
) -> dict[str, Any]:
    """
    Process a chat message and return AI response with potential tool calls.

    Args:
        message: User's message
        session_id: Session identifier (for future use)
        conversation_history: Previous messages in conversation

    Returns:
        dict with 'content' (str) and optionally 'tool_calls' (list)
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Add conversation history if provided
    if conversation_history:
        messages.extend(conversation_history)

    # Add current user message
    messages.append({"role": "user", "content": message})

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",  # Cost-effective for POC
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            max_tokens=500,
            temperature=0.7,
        )

        assistant_message = response.choices[0].message

        result = {
            "content": assistant_message.content or "",
            "tool_calls": None,
            "finish_reason": response.choices[0].finish_reason,
        }

        # Extract tool calls if present
        if assistant_message.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments),
                }
                for tc in assistant_message.tool_calls
            ]

        return result

    except Exception as e:
        return {
            "content": "I'm having trouble processing your request. Please try again.",
            "tool_calls": None,
            "error": str(e),
        }


async def get_tool_response(tool_name: str, tool_args: dict) -> str:
    """
    Execute a tool and return the result as a string for the LLM.
    This is a placeholder - actual implementation will connect to database.
    """
    if tool_name == "track_product":
        return f"Successfully added '{tool_args['product_name']}' to your watchlist with target price ${tool_args['target_price']:.2f}"

    elif tool_name == "get_recommendations":
        category = tool_args.get("category", "Electronics")
        max_price = tool_args.get("max_price", 1000)
        return f"Found recommendations in {category} under ${max_price:.2f}: [Placeholder - will connect to database]"

    elif tool_name == "list_tracked_items":
        return "Currently tracking: [Placeholder - will connect to database]"

    return "Unknown tool"
