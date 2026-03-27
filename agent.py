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
                "properties": {
                    "user": {"type": "string"},
                    "movie": {"type": "string"},
                    "expectation": {"type": "string"},
                    "watch_time": {"type": "string"},
                },
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
    {
        "type": "function",
        "function": {
            "name": "filter_movies",
            "description": "Get top movies by genre or keyword",
            "parameters": {
                "type": "object",
                "properties": {"keyword": {"type": "string"}},
                "required": ["keyword"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "top_movies",
            "description": "Get top rated movies optionally filtered by keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {"type": "string"},
                    "top_n": {"type": "integer"},
                    "verbose": {"type": "boolean"},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_movie_details",
            "description": "Get full details of a movie",
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
            "name": "add_user",
            "description": "Create a new user",
            "parameters": {
                "type": "object",
                "properties": {"username": {"type": "string"}},
                "required": ["username"],
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

    elif name == "filter_movies":
        return services.filter_movies(**args)

    elif name == "top_movies":
        return services.top_movies(**args)

    elif name == "get_movie_details":
        return services.get_movie_details(**args)

    elif name == "add_user":
        return services.add_user(**args)

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
                    "You are an intelligent movie assistant that helps users manage movies.\n\n"
                    "You can:\n"
                    "- Recommend movies based on similarity\n"
                    "- Search movies from database\n"
                    "- Add movies with metadata (genre, cast, director)\n"
                    "- Manage watchlist\n"
                    "- Mark movies as watched\n\n"
                    "Rules:\n"
                    "1. Always use tools when user asks for actions (add, search, recommend, etc.)\n"
                    "2. Be precise in extracting movie names and user names\n"
                    "3. If metadata is mentioned, include it\n"
                    "4. If user intent is unclear, ask a clarifying question\n"
                    "5. Never hallucinate movie existence—use tools to verify\n"
                    '6. If user asks for "top N movies", interpret it as highest rated movies\n'
                    "7. If user provides a keyword (like horror, action), filter using that\n"
                    '8. If user says "with details", "verbose", or "explain", set verbose=True\n'
                    "9. If user mentions time (e.g., tomorrow, tonight, 7pm), include it as watch_time\n"
                    "10. If user mentions expectation, include it as expectation\n"
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

        # 🧠 CLARIFICATION LOGIC

        # add_movie requires movie_title
        if name == "add_movie" and not args.get("movie_title"):
            return "What is the movie name you want to add?"

        # add_to_watchlist requires user + movie
        if name == "add_to_watchlist":
            if not args.get("user"):
                return "Which user should I add the movie for?"
            if not args.get("movie"):
                return "Which movie do you want to add to the watchlist?"

        # mark_as_watched requires user + movie
        if name == "mark_as_watched":
            if not args.get("user"):
                return "Which user watched the movie?"
            if not args.get("movie"):
                return "Which movie should I mark as watched?"

        # get_watchlist requires user
        if name == "get_watchlist" and not args.get("user"):
            return "Whose watchlist do you want to see?"

        # ✅ If all arguments present → proceed
        result = call_function(name, args)

        log_interaction(query, name, result)

        # For debugging
        # return f"[Tool: {name}] → {result}"
        # If it's structured (list of dicts), return as-is
        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            return result

        # single structured object
        if isinstance(result, dict):
            return result
        # If it's a normal list (strings), format nicely
        if isinstance(result, list):
            return [f"{r}" for r in result]

        return result

    return message.content
