"""OpenAI LLM service with tool calling for intent extraction."""

import json
from typing import Any
from openai import AsyncOpenAI  # type: ignore
from app.config import get_settings
from app.services.products import (
    search_products,
    get_products_by_category,
    create_tracked_item,
    get_tracked_items,
)

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)

# System prompt with guardrails
SYSTEM_PROMPT = """You are DealHunter, a product deal tracking assistant.

RULES:
- You help users track product prices and get recommendations.
- You do NOT track flights or travel - politely redirect to product deals.
- You NEVER hallucinate prices - use tools to get real data.
- You are concise - max 2-3 sentences per response.
- ALWAYS call the track_product tool when user mentions tracking ANY product with a price. Do NOT ask for clarification - just use the product name they gave you.
- If user says "Track X under $Y", immediately call track_product with product_name=X and target_price=Y.

Available products in our database: Samsung TV, Sony Headphones, MacBook Laptop.

Available actions:
- Track a product at a target price (use track_product tool)
- Get product recommendations by category (use get_recommendations tool)
- List currently tracked items (use list_tracked_items tool)"""

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
    Connects to Supabase for actual data operations.
    """
    try:
        if tool_name == "track_product":
            product_name = tool_args["product_name"]
            target_price = tool_args["target_price"]

            products = search_products(product_name)

            if not products:
                return f"I couldn't find a product matching '{product_name}' in our database. We currently have TVs, Headphones, and Laptops available."

            product = products[0]

            tracked = create_tracked_item(
                product_id=product["id"], target_price=target_price
            )

            if tracked:
                return f"Great! I'm now tracking '{product['name']}' (currently ${product['current_price']:.2f}) and will alert you when it drops below ${target_price:.2f}."
            else:
                return f"I found '{product['name']}' but had trouble adding it to your watchlist. Please try again."

        elif tool_name == "get_recommendations":
            category = tool_args.get("category", "Electronics")
            max_price = tool_args.get("max_price")

            products = get_products_by_category(category, max_price)

            if not products:
                return (
                    f"I couldn't find any products in the '{category}' category"
                    + (f" under ${max_price:.2f}" if max_price else "")
                    + "."
                )

            product_list = "\n".join(
                [f"- {p['name']}: ${p['current_price']:.2f}" for p in products]
            )
            return f"Here are some {category} deals:\n{product_list}"

        elif tool_name == "list_tracked_items":
            items = get_tracked_items()

            if not items:
                return "You're not tracking any products yet. Try saying 'Track [product name] under $[price]' to get started!"

            item_list = "\n".join(
                [
                    f"- {item['products']['name']}: watching for ${item['target_price']:.2f} (currently ${item['products']['current_price']:.2f})"
                    for item in items
                    if item.get("products")
                ]
            )
            return f"You're currently tracking:\n{item_list}"

        return "Unknown tool"

    except Exception as e:
        return f"I encountered an error: {str(e)}. Please try again."
