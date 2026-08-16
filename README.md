# Hermes Plex + Tautulli

A read-only [Hermes Agent](https://github.com/NousResearch/hermes-agent) plugin that lets you ask natural-language questions about the media available on your Plex server and the playback history recorded by Tautulli.

It can search Plex libraries, list recently added media, inspect current streaming activity, retrieve play history, and summarize viewing statistics. It does not delete media, start playback, refresh libraries, change server settings, or expose stored Tautulli tokens and email addresses.

## Example prompts

- “Do I have *The Matrix* in my Plex library?”
- “Which *Star Trek* series are available?”
- “What are the 20 most recently added movies and shows?”
- “What did we watch last weekend?”
- “What was the last episode of *Severance* we watched?”
- “Show me the most recent plays and whether each direct-played or transcoded.”
- “What is currently streaming on Plex?”
- “Which movies and shows were watched most often in the last 30 days?”
- “Who watched the most Plex content this month?”

## Installation

The preferred installation method is the Hermes Web UI:

1. Open the Hermes dashboard and go to **Plugins**. You can also open the page directly at `http://<HERMES-HOST>:9119/plugins`.
2. Enter `nathanpond/hermes-plex-tautulli` in the plugin installation field.
3. Select **Install**, then enable the plugin if it is not enabled automatically.
4. **Start a new chat session.** Existing sessions retain the tool list they were created with and will not see newly enabled plugin tools.

Use the dedicated Plugins page rather than asking the chat agent to install the plugin. A conversational request may cause the agent to improvise shell commands instead of invoking Hermes's native plugin manager.

### Console fallback

If installation through the Web UI is unavailable or fails, open a terminal in the Hermes container and run:

```bash
hermes plugins install nathanpond/hermes-plex-tautulli --enable
```

The installer prompts for any required settings that are not already present in the Hermes environment:

| Variable | Description | Example |
| --- | --- | --- |
| `PLEX_URL` | Base URL of Plex Media Server | `http://192.168.1.10:32400` |
| `PLEX_TOKEN` | Plex `X-Plex-Token` | Secret |
| `TAUTULLI_URL` | Base URL of Tautulli | `http://192.168.1.10:8181` |
| `TAUTULLI_API_KEY` | Tautulli API key | Secret |

After installation, start a new chat session and confirm that the plugin loaded by asking:

> List my Plex libraries and their media types.

You can also confirm installation from the dashboard's **Plugins** page or, from a terminal, with:

```bash
hermes plugins list
```

A gateway or container restart is not normally required. Use it only as a troubleshooting step if the plugin tools are still unavailable in a new chat session.

### Updating

```bash
hermes plugins update plex-tautulli
```

### Removing

```bash
hermes plugins remove plex-tautulli
```

## Getting credentials

### Plex token

Plex documents several ways to locate an `X-Plex-Token`. One common method is to open an item in Plex Web, choose **Get Info**, select **View XML**, and copy the `X-Plex-Token` value from the resulting URL.

See [Finding an authentication token / X-Plex-Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

### Tautulli API key

In Tautulli, open **Settings → Web Interface**, enable API access if necessary, and copy the API key.

## Tools

| Tool | Purpose |
| --- | --- |
| `plex_list_libraries` | List Plex library sections and media types |
| `plex_search_library` | Search media already available in Plex |
| `plex_recently_added` | List recently added media |
| `tautulli_history` | Query filtered playback history |
| `tautulli_activity` | Inspect current streaming sessions |
| `tautulli_home_stats` | Retrieve top media, users, and platform statistics |
| `tautulli_list_users` | List user display names and IDs without tokens or email addresses |

## Security and privacy

- All plugin operations use HTTP `GET` requests.
- The plugin does not provide delete, playback, scan, refresh, or configuration tools.
- Plex credentials are sent in the `X-Plex-Token` request header.
- Tautulli credentials are sent to its `/api/v2` endpoint as required by the Tautulli API.
- History and activity results omit IP addresses.
- User results omit email addresses and Tautulli's stored Plex server tokens.
- Credentials remain in the Hermes environment and are never returned in tool results.

Use HTTPS or a trusted private network when Plex or Tautulli is hosted on another machine.

## Requirements

- Hermes Agent with plugin support
- Plex Media Server reachable from Hermes
- Tautulli reachable from Hermes and connected to the same Plex server
- Python standard library only; no additional packages are required

## Development

The plugin uses Hermes's native Python plugin interface. The manifest declares required environment variables, `schemas.py` defines model-facing tools, `tools.py` implements read-only API calls, and `__init__.py` registers the tools with the `plex_tautulli` toolset.

## License

Released under the [MIT License](LICENSE).
