"""OpenAI LLM service with tool calling for intent extraction."""

import json
import logging
from typing import Any
from openai import AsyncOpenAI  # type: ignore
from app.config import get_settings
from app.services.products import (
    search_products,
    search_catalog,
    get_products_by_category,
    get_product_categories,
    create_tracked_item,
    get_tracked_items,
    get_tracked_item_by_product_id,
    update_tracked_item_target_price,
)

logger = logging.getLogger(__name__)

settings = get_settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)

# System prompt with guardrails
SYSTEM_PROMPT = """You are DealHunter, a product deal tracking assistant.

RULES:
- You help users track product prices and find deals across our product catalog.
- You do NOT track flights or travel - politely redirect to product deals.
- You NEVER hallucinate prices - use tools to get real data.
- You are concise - max 2-3 sentences per response.
- ALWAYS call the track_product tool when user mentions tracking ANY product with a price. Do NOT ask for clarification - just use the product name they gave you.
- If user says "Track X under $Y", immediately call track_product with product_name=X and target_price=Y.
- When a user asks about products, categories, or what's available, use the search_catalog tool to find matching products.
- We have a large catalog spanning many categories including TVs, Laptops, Headphones, Earbuds, Speakers, Tablets, Phones, Gaming, Home, Fitness, and Cameras.

Available actions:
- Search our product catalog by name, category, or price range (use search_catalog tool)
- Track a product at a target price (use track_product tool)
- Get product recommendations by category (use get_recommendations tool)
- List currently tracked items (use list_tracked_items tool)"""

# Tool definitions for OpenAI function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_catalog",
            "description": "Search the product catalog by name, category, and/or price range. Use this when users ask about available products, want to browse, or search for something specific.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term to match against product names (e.g., 'Sony', 'MacBook', 'vacuum')",
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category: TV, Laptop, Headphones, Earbuds, Speakers, Tablet, Phone, Gaming, Home, Fitness, Camera",
                    },
                    "min_price": {
                        "type": "number",
                        "description": "Minimum price in USD",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in USD",
                    },
                },
                "required": [],
            },
        },
    },
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
                        "description": "The name of the product to track (e.g., 'Sony WH-1000XM5', 'MacBook Air', 'Dyson vacuum')",
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
                        "description": "Product category (e.g., 'TV', 'Headphones', 'Laptop', 'Gaming', 'Fitness', 'Home')",
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
            parsed_tool_calls = []
            for tc in assistant_message.tool_calls:
                try:
                    args = json.loads(tc.function.arguments)
                except (json.JSONDecodeError, TypeError) as e:
                    logger.error("Failed to parse tool arguments for %s: %s", tc.function.name, e)
                    args = {}
                parsed_tool_calls.append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": args,
                })
            result["tool_calls"] = parsed_tool_calls

        return result

    except Exception as e:
        return {
            "content": "I'm having trouble processing your request. Please try again.",
            "tool_calls": None,
            "error": str(e),
        }


async def get_tool_response(
    tool_name: str, tool_args: dict, user_id: str | None = None, session=None
) -> str:
    """
    Execute a tool and return the result as a string for the LLM.
    Connects to PostgreSQL via SQLAlchemy for data operations.
    """
    try:
        if tool_name == "search_catalog":
            query = tool_args.get("query")
            category = tool_args.get("category")
            min_price = tool_args.get("min_price")
            max_price = tool_args.get("max_price")

            if not query and not category and min_price is None and max_price is None:
                # No filters — return categories overview
                categories = await get_product_categories(session)
                return f"We have products across these categories: {', '.join(categories)}. What are you looking for?"

            products = await search_catalog(
                session,
                query=query,
                category=category,
                min_price=min_price,
                max_price=max_price,
            )

            if not products:
                categories = await get_product_categories(session)
                return (
                    f"No products found matching your search. "
                    f"Try browsing by category: {', '.join(categories)}."
                )

            product_list = "\n".join(
                [f"- {p['name']} ({p['category']}): ${p['current_price']:.2f}" for p in products]
            )
            return f"Found {len(products)} product(s):\n{product_list}"

        elif tool_name == "track_product":
            product_name = tool_args.get("product_name")
            target_price = tool_args.get("target_price")

            if not product_name or not isinstance(product_name, str):
                return "I need a product name to track. Try saying 'Track Sony headphones under $300'."
            if target_price is None or not isinstance(target_price, (int, float)) or target_price <= 0:
                return "I need a valid target price. Try saying 'Track Sony headphones under $300'."

            products = await search_products(session, product_name)

            if not products:
                return f"I couldn't find a product matching '{product_name}' in our catalog. Try searching with the product name or browsing by category."

            product = products[0]

            # Check if already tracked by this user
            existing = await get_tracked_item_by_product_id(session, product["id"], user_id=user_id)
            if existing:
                await update_tracked_item_target_price(session, existing["id"], target_price)
                return f"Updated tracking for '{product['name']}' (currently ${product['current_price']:.2f}). New alert target: ${target_price:.2f}."

            tracked = await create_tracked_item(
                session, product_id=product["id"], target_price=target_price, user_id=user_id
            )

            if tracked:
                return f"Great! I'm now tracking '{product['name']}' (currently ${product['current_price']:.2f}) and will alert you when it drops below ${target_price:.2f}."
            else:
                return f"I found '{product['name']}' but had trouble adding it to your watchlist. Please try again."

        elif tool_name == "get_recommendations":
            category = tool_args.get("category", "Electronics")
            max_price = tool_args.get("max_price")

            if max_price is not None:
                try:
                    max_price = float(max_price)
                    if max_price <= 0:
                        max_price = None
                except (TypeError, ValueError):
                    max_price = None

            products = await get_products_by_category(session, category, max_price)

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
            items = await get_tracked_items(session, user_id=user_id)

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

        logger.warning("Unknown tool called: %s with args: %s", tool_name, tool_args)
        return "Unknown tool"

    except Exception as e:
        logger.error("Tool execution error for %s: %s", tool_name, e)
        return f"I encountered an error: {str(e)}. Please try again."
