"""Tool schemas presented to the language model."""

PLEX_LIST_LIBRARIES = {
    "name": "plex_list_libraries",
    "description": "List the Plex media libraries and their section IDs. Read-only.",
    "parameters": {"type": "object", "properties": {}},
}

PLEX_SEARCH_LIBRARY = {
    "name": "plex_search_library",
    "description": (
        "Search the user's Plex server for movies, shows, seasons, episodes, "
        "artists, albums, or tracks already present in the library. Read-only."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Title or name to search for."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 20},
        },
        "required": ["query"],
    },
}

PLEX_RECENTLY_ADDED = {
    "name": "plex_recently_added",
    "description": "Return media recently added to Plex, optionally from one library. Read-only.",
    "parameters": {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "minimum": 1, "maximum": 50, "default": 20},
            "section_id": {"type": "string", "description": "Optional Plex library section ID."},
        },
    },
}

TAUTULLI_HISTORY = {
    "name": "tautulli_history",
    "description": (
        "Query Plex play history from Tautulli. Use for what was watched, who watched it, "
        "when it was watched, playback duration, platform, player, or transcode decision. "
        "For requests such as past N days, weeks, or months, ALWAYS convert the period to days "
        "and use the days parameter. Use after and before only for explicit calendar ranges. "
        "Compare returned_count with records_filtered and continue with offset when has_more is true. Read-only."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "days": {"type": "integer", "minimum": 1, "maximum": 3650, "description": "Inclusive recent-history window. Use 7 for the past week, 14 for the past two weeks, 30 for the past month, and so on."},
            "after": {"type": "string", "description": "Optional inclusive earliest date in YYYY-MM-DD format. Use for an explicit 'since YYYY-MM-DD' request, not relative periods."},
            "before": {"type": "string", "description": "Optional inclusive latest date in YYYY-MM-DD format."},
            "user": {"type": "string", "description": "Optional Plex friendly name or username."},
            "search": {"type": "string", "description": "Optional title/history search text."},
            "media_type": {"type": "string", "enum": ["movie", "episode", "track", "live"]},
            "section_id": {"type": "integer", "description": "Optional Plex library section ID."},
            "transcode_decision": {"type": "string", "enum": ["direct play", "copy", "transcode"]},
            "grouping": {"type": "integer", "enum": [0, 1], "default": 0, "description": "0 returns every playback session; 1 groups related history rows."},
            "offset": {"type": "integer", "minimum": 0, "default": 0, "description": "Row offset for retrieving the next page when has_more is true."},
            "limit": {"type": "integer", "minimum": 1, "maximum": 500, "default": 500},
        },
    },
}

TAUTULLI_ACTIVITY = {
    "name": "tautulli_activity",
    "description": "Return current Plex streaming activity from Tautulli. Read-only.",
    "parameters": {"type": "object", "properties": {}},
}

TAUTULLI_HOME_STATS = {
    "name": "tautulli_home_stats",
    "description": (
        "Return Tautulli viewing statistics such as top movies, shows, users, and platforms "
        "over a selected number of days. Read-only."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "days": {"type": "integer", "minimum": 1, "maximum": 3650, "default": 30},
            "stats_type": {"type": "string", "enum": ["plays", "duration"], "default": "plays"},
            "count": {"type": "integer", "minimum": 1, "maximum": 25, "default": 10},
        },
    },
}

TAUTULLI_LIST_USERS = {
    "name": "tautulli_list_users",
    "description": "List Plex user display names and IDs known to Tautulli. Excludes email and tokens. Read-only.",
    "parameters": {"type": "object", "properties": {}},
}
