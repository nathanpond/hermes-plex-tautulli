"""Read-only HTTP handlers for Plex and Tautulli."""

import json
import os
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


def _result(payload):
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _required_env(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value.rstrip("/") if name.endswith("_URL") else value


def _clamp(value, low, high, default):
    try:
        return max(low, min(high, int(value)))
    except (TypeError, ValueError):
        return default


def _http_json(url, headers=None):
    request = urllib.request.Request(url, headers=headers or {}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} from media service") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Unable to reach media service: {exc.reason}") from exc


def _plex_xml(path, params=None):
    base = _required_env("PLEX_URL")
    token = _required_env("PLEX_TOKEN")
    query = urllib.parse.urlencode(params or {})
    url = f"{base}{path}" + (f"?{query}" if query else "")
    request = urllib.request.Request(url, headers={"X-Plex-Token": token}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return ET.fromstring(response.read())
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Plex returned HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Unable to reach Plex: {exc.reason}") from exc
    except ET.ParseError as exc:
        raise RuntimeError("Plex returned invalid XML") from exc


def _tautulli(command, params=None):
    base = _required_env("TAUTULLI_URL")
    api_key = _required_env("TAUTULLI_API_KEY")
    query = {"apikey": api_key, "cmd": command}
    query.update({key: value for key, value in (params or {}).items() if value not in (None, "")})
    payload = _http_json(f"{base}/api/v2?{urllib.parse.urlencode(query)}")
    response = payload.get("response", {})
    if response.get("result") != "success":
        raise RuntimeError(response.get("message") or f"Tautulli command {command} failed")
    return response.get("data")


def _plex_item(element):
    attributes = element.attrib
    allowed = (
        "ratingKey", "type", "title", "titleSort", "year", "parentTitle",
        "grandparentTitle", "librarySectionTitle", "librarySectionID", "summary",
        "contentRating", "rating", "audienceRating", "duration", "viewCount",
        "lastViewedAt", "addedAt", "originallyAvailableAt", "index", "parentIndex",
    )
    return {key: attributes[key] for key in allowed if attributes.get(key) not in (None, "")}


def plex_list_libraries(params, **kwargs):
    del params, kwargs
    root = _plex_xml("/library/sections")
    libraries = []
    for directory in root.findall("Directory"):
        libraries.append({
            key: directory.attrib[key]
            for key in ("key", "title", "type", "agent", "scanner", "language", "updatedAt")
            if directory.attrib.get(key) not in (None, "")
        })
    return _result({"success": True, "libraries": libraries})


def plex_search_library(params, **kwargs):
    del kwargs
    query = str(params.get("query", "")).strip()
    if not query:
        return _result({"success": False, "error": "query is required"})
    limit = _clamp(params.get("limit"), 1, 50, 20)
    root = _plex_xml("/hubs/search", {"query": query, "limit": limit})
    items = []
    for hub in root.findall("Hub"):
        for child in list(hub):
            if child.tag in ("Video", "Directory", "Track"):
                item = _plex_item(child)
                item["hub"] = hub.attrib.get("title") or hub.attrib.get("type")
                items.append(item)
                if len(items) >= limit:
                    break
        if len(items) >= limit:
            break
    return _result({"success": True, "query": query, "count": len(items), "items": items})


def plex_recently_added(params, **kwargs):
    del kwargs
    limit = _clamp(params.get("limit"), 1, 50, 20)
    section_id = str(params.get("section_id", "")).strip()
    path = f"/library/sections/{section_id}/recentlyAdded" if section_id else "/library/recentlyAdded"
    root = _plex_xml(path, {"X-Plex-Container-Start": 0, "X-Plex-Container-Size": limit})
    items = [_plex_item(child) for child in list(root) if child.tag in ("Video", "Directory", "Track")]
    return _result({"success": True, "count": len(items), "items": items[:limit]})


def _safe_history_row(row):
    allowed = (
        "row_id", "date", "started", "stopped", "duration", "paused_counter",
        "user", "friendly_name", "full_title", "title", "parent_title",
        "grandparent_title", "year", "media_type", "rating_key", "section_id",
        "platform", "player", "product", "quality_profile", "video_decision",
        "audio_decision", "transcode_decision", "watched_status", "percent_complete",
    )
    return {key: row[key] for key in allowed if row.get(key) not in (None, "")}


def tautulli_history(params, **kwargs):
    del kwargs
    limit = _clamp(params.get("limit"), 1, 500, 100)
    offset = _clamp(params.get("offset"), 0, 1000000000, 0)
    grouping = _clamp(params.get("grouping"), 0, 1, 0)
    query = {
        "grouping": grouping,
        "order_column": "date",
        "order_dir": "desc",
        "start": offset,
        "length": limit,
        "start_date": params.get("start_date"),
        "after": params.get("after"),
        "before": params.get("before"),
        "user": params.get("user"),
        "search": params.get("search"),
        "media_type": params.get("media_type"),
        "section_id": params.get("section_id"),
        "transcode_decision": params.get("transcode_decision"),
    }
    data = _tautulli("get_history", query) or {}
    rows = [_safe_history_row(row) for row in data.get("data", [])[:limit]]
    records_filtered = data.get("recordsFiltered")
    try:
        has_more = offset + len(rows) < int(records_filtered)
    except (TypeError, ValueError):
        has_more = False
    return _result({
        "success": True,
        "records_total": data.get("recordsTotal"),
        "records_filtered": records_filtered,
        "returned_count": len(rows),
        "offset": offset,
        "has_more": has_more,
        "grouping": grouping,
        "total_duration": data.get("total_duration"),
        "filter_duration": data.get("filter_duration"),
        "history": rows,
    })


def tautulli_activity(params, **kwargs):
    del params, kwargs
    data = _tautulli("get_activity") or {}
    allowed = (
        "session_key", "user", "friendly_name", "full_title", "title", "parent_title",
        "grandparent_title", "media_type", "year", "platform", "player", "product",
        "state", "progress_percent", "duration", "view_offset", "quality_profile",
        "video_decision", "audio_decision", "transcode_decision", "stream_video_resolution",
    )
    sessions = [
        {key: row[key] for key in allowed if row.get(key) not in (None, "")}
        for row in data.get("sessions", [])
    ]
    return _result({
        "success": True,
        "stream_count": data.get("stream_count", len(sessions)),
        "total_bandwidth": data.get("total_bandwidth"),
        "sessions": sessions,
    })


def tautulli_home_stats(params, **kwargs):
    del kwargs
    days = _clamp(params.get("days"), 1, 3650, 30)
    count = _clamp(params.get("count"), 1, 25, 10)
    stats_type = params.get("stats_type") if params.get("stats_type") in ("plays", "duration") else "plays"
    data = _tautulli("get_home_stats", {
        "grouping": 1,
        "time_range": days,
        "stats_type": stats_type,
        "stats_count": count,
    }) or []
    safe_stats = []
    row_fields = (
        "title", "full_title", "grandparent_title", "friendly_name", "platform",
        "total_plays", "total_duration", "users_watched", "rating_key", "year",
        "media_type", "content_rating",
    )
    for statistic in data:
        safe_stats.append({
            "stat_id": statistic.get("stat_id"),
            "stat_type": statistic.get("stat_type"),
            "rows": [
                {key: row[key] for key in row_fields if row.get(key) not in (None, "")}
                for row in statistic.get("rows", [])[:count]
            ],
        })
    return _result({"success": True, "days": days, "stats_type": stats_type, "statistics": safe_stats})


def tautulli_list_users(params, **kwargs):
    del params, kwargs
    data = _tautulli("get_user_names") or []
    users = [
        {key: row[key] for key in ("friendly_name", "user_id") if row.get(key) not in (None, "")}
        for row in data
    ]
    return _result({"success": True, "users": users})
