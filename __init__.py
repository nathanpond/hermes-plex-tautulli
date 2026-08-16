"""Read-only Plex and Tautulli integration for Hermes Agent."""

from . import schemas, tools


def register(ctx):
    registrations = (
        (schemas.PLEX_LIST_LIBRARIES, tools.plex_list_libraries),
        (schemas.PLEX_SEARCH_LIBRARY, tools.plex_search_library),
        (schemas.PLEX_RECENTLY_ADDED, tools.plex_recently_added),
        (schemas.TAUTULLI_HISTORY, tools.tautulli_history),
        (schemas.TAUTULLI_ACTIVITY, tools.tautulli_activity),
        (schemas.TAUTULLI_HOME_STATS, tools.tautulli_home_stats),
        (schemas.TAUTULLI_LIST_USERS, tools.tautulli_list_users),
    )
    for schema, handler in registrations:
        ctx.register_tool(
            name=schema["name"],
            toolset="plex_tautulli",
            schema=schema,
            handler=handler,
        )
