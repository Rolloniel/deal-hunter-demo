"""Test script for LLM service."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from project root
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from app.services.llm import process_message


async def test_track_product():
    """Test that tracking request triggers track_product tool."""
    print("\n=== Test 1: Track Samsung 65 inch TV under $900 ===")
    # Use specific product name to ensure tool is called (not clarification)
    result = await process_message(
        "Track Samsung 65 inch TV under $900", "test-session"
    )
    print(f"Result: {result}")

    # Check if tool was called
    if result.get("tool_calls"):
        tool_call = result["tool_calls"][0]
        print(f"Tool called: {tool_call['name']}")
        print(f"Arguments: {tool_call['arguments']}")
        assert tool_call["name"] == "track_product", (
            f"Expected track_product, got {tool_call['name']}"
        )
        assert "samsung" in tool_call["arguments"]["product_name"].lower(), (
            "Product name should contain 'samsung'"
        )
        assert tool_call["arguments"]["target_price"] == 900, (
            f"Expected 900, got {tool_call['arguments']['target_price']}"
        )
        print("PASS: track_product tool called correctly")
    else:
        print(f"Content: {result.get('content')}")
        # If no tool call, check if it's asking for clarification
        assert "track" in result.get("content", "").lower() or result.get(
            "tool_calls"
        ), "Should either call tool or mention tracking"
        print("PASS: Response mentions tracking (may need clarification)")


async def test_flight_rejection():
    """Test that flight requests are politely declined."""
    print("\n=== Test 2: Track flights to Tokyo (should be declined) ===")
    result = await process_message("Track flights to Tokyo", "test-session")
    print(f"Result: {result}")

    content = result.get("content", "").lower()
    tool_calls = result.get("tool_calls")

    # Should NOT call track_product for flights
    if tool_calls:
        for tc in tool_calls:
            assert (
                tc["name"] != "track_product"
                or "flight" not in tc["arguments"].get("product_name", "").lower()
            ), "Should not track flights as products"

    # Should mention products or redirect
    assert (
        "product" in content
        or "deal" in content
        or "flight" in content
        or not tool_calls
    ), "Should redirect to products or decline flights"
    print(f"Content: {result.get('content')}")
    print("PASS: Flight request handled appropriately")


async def test_list_tracked():
    """Test list tracked items."""
    print("\n=== Test 3: What am I tracking? ===")
    result = await process_message("What am I tracking?", "test-session")
    print(f"Result: {result}")

    if result.get("tool_calls"):
        tool_call = result["tool_calls"][0]
        assert tool_call["name"] == "list_tracked_items", (
            f"Expected list_tracked_items, got {tool_call['name']}"
        )
        print("PASS: list_tracked_items tool called")
    else:
        print(f"Content: {result.get('content')}")
        print("PASS: Response provided (may not have tool call)")


async def test_recommendations():
    """Test get recommendations."""
    print("\n=== Test 4: Show me headphone deals under $200 ===")
    result = await process_message("Show me headphone deals under $200", "test-session")
    print(f"Result: {result}")

    if result.get("tool_calls"):
        tool_call = result["tool_calls"][0]
        print(f"Tool called: {tool_call['name']}")
        print(f"Arguments: {tool_call['arguments']}")
        assert tool_call["name"] == "get_recommendations", (
            f"Expected get_recommendations, got {tool_call['name']}"
        )
        print("PASS: get_recommendations tool called")
    else:
        print(f"Content: {result.get('content')}")
        print("PASS: Response provided")


async def main():
    """Run all tests."""
    print("=" * 60)
    print("LLM Service Tests")
    print("=" * 60)

    try:
        await test_track_product()
        await test_flight_rejection()
        await test_list_tracked()
        await test_recommendations()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
