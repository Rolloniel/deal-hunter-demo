"""Chat router with SSE streaming."""

import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import ChatMessage
from app.services.llm import process_message, get_tool_response

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def generate_stream(message: str, session_id: str):
    """Generate SSE stream for chat response."""
    try:
        # Get initial response from LLM
        result = await process_message(message, session_id)

        # Handle tool calls if present
        if result.get("tool_calls"):
            for tool_call in result["tool_calls"]:
                tool_result = await get_tool_response(
                    tool_call["name"], tool_call["arguments"]
                )
                # Stream tool execution status
                yield f"data: {json.dumps({'type': 'tool', 'name': tool_call['name']})}\n\n"

                # Get final response after tool execution
                # In a real implementation, we'd pass tool results back to LLM
                # For POC, we'll use the tool result directly
                final_response = tool_result

                # Stream the response in chunks
                words = final_response.split()
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"
        else:
            # No tool calls - stream the content directly
            content = result.get("content", "")
            if content:
                words = content.split()
                for i, word in enumerate(words):
                    chunk = word + (" " if i < len(words) - 1 else "")
                    yield f"data: {json.dumps({'type': 'text', 'content': chunk})}\n\n"

        # Send done signal
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@router.post("")
async def chat(request: ChatMessage):
    """
    Chat endpoint with SSE streaming.

    Accepts a message and session_id, returns a stream of text chunks.
    Tool calls are handled internally and not exposed to the client.
    """
    return StreamingResponse(
        generate_stream(request.message, request.session_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        },
    )


@router.post("/sync")
async def chat_sync(request: ChatMessage):
    """
    Non-streaming chat endpoint for testing.
    Returns the complete response at once.
    """
    result = await process_message(request.message, request.session_id)

    # Handle tool calls
    if result.get("tool_calls"):
        tool_responses = []
        for tool_call in result["tool_calls"]:
            tool_result = await get_tool_response(
                tool_call["name"], tool_call["arguments"]
            )
            tool_responses.append({"tool": tool_call["name"], "result": tool_result})
        return {
            "response": tool_responses[0]["result"] if tool_responses else "",
            "tool_calls": result["tool_calls"],
        }

    return {"response": result.get("content", "")}
