import json
import os

from dotenv import load_dotenv
from openai import OpenAI

import services

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# TOOLS DEFINITION
# =========================

tools = [
    {
        "type": "function",
        "function": {
            "name": "recommend_movies",
            "description": "Recommend similar movies based on a given movie title",
            "parameters": {
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_movies",
            "description": "Search movies by name",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_to_watchlist",
            "description": "Add a movie to a user's watchlist",
            "parameters": {
                "type": "object",
                "properties": {"user": {"type": "string"}, "movie": {"type": "string"}},
                "required": ["user", "movie"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_watchlist",
            "description": "Get all movies in a user's watchlist",
            "parameters": {
                "type": "object",
                "properties": {"user": {"type": "string"}},
                "required": ["user"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "mark_as_watched",
            "description": "Mark a movie as watched",
            "parameters": {
                "type": "object",
                "properties": {"user": {"type": "string"}, "movie": {"type": "string"}},
                "required": ["user", "movie"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_movie",
            "description": "Add a new movie to the database",
            "parameters": {
                "type": "object",
                "properties": {"movie_title": {"type": "string"}},
                "required": ["movie_title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_movie",
            "description": "Add a new movie with optional metadata",
            "parameters": {
                "type": "object",
                "properties": {
                    "movie_title": {"type": "string"},
                    "genres": {"type": "string"},
                    "keywords": {"type": "string"},
                    "cast_members": {"type": "string"},
                    "director": {"type": "string"},
                },
                "required": ["movie_title"],
            },
        },
    },
]

# =========================
# FUNCTION EXECUTOR
# =========================


def call_function(name, args):
    if name == "recommend_movies":
        return services.recommend_movies(**args)

    elif name == "search_movies":
        return services.search_movies(**args)

    elif name == "add_to_watchlist":
        return services.add_to_watchlist(**args)

    elif name == "get_watchlist":
        return services.get_watchlist(**args)

    elif name == "mark_as_watched":
        return services.mark_as_watched(**args)

    elif name == "add_movie":
        return services.add_movie(**args)

    return "Unknown function"


# =========================
# LOGGING
# =========================


def log_interaction(query, tool, result):
    os.makedirs("logs", exist_ok=True)
    with open("logs/interactions.log", "a") as f:
        f.write(f"{query} | {tool} | {result}\n")


# =========================
# AGENT CORE
# =========================


def run_agent(query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a movie assistant. Use tools when appropriate. "
                    "If the user asks to add or view watchlist, always use tools."
                ),
            },
            {"role": "user", "content": query},
        ],
        tools=tools,
    )

    message = response.choices[0].message

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        result = call_function(name, args)

        log_interaction(query, name, result)

        # For debugging
        # return f"[Tool: {name}] → {result}"
        if isinstance(result, list):
            return "\n".join(result)

        return result

    return message.content
