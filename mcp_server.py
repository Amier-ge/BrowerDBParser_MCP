import sqlite3
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("browser-db-parser")

SERVER_INFO = {
    "name": "browser-db-parser",
    "version": "1.0.0",
    "description": "Browser history database parser MCP server. Parses SQLite history databases from Chromium, Firefox, and Safari browsers.",
    "supported_browsers": ["Chromium-based (Chrome, Edge, Brave, etc.)", "Mozilla-based (Firefox)", "Safari-based"],
    "tools": [
        {
            "name": "get_info",
            "description": "Returns MCP server information including name, version, description, and available tools"
        },
        {
            "name": "parse_history",
            "description": "Parses browser history SQLite database file and returns browsing/download history",
            "parameters": {
                "history_file_path": "Path to the browser history SQLite database file"
            }
        }
    ]
}


@mcp.tool()
def get_info() -> str:
    """Returns MCP server information including name, version, description, and available tools."""
    return json.dumps(SERVER_INFO, ensure_ascii=False, indent=2)


def detect_browser_type(cursor) -> str | None:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    result = str(cursor.fetchall())

    if "moz" in result:
        return "Mozilla-based"
    elif "downloads_slices" in result:
        return "Chromium-based"
    elif "history_visits" in result:
        return "Safari-based"
    return None


def parse_chromium(cursor) -> dict:
    # Browsing history
    cursor.execute("""
        SELECT datetime(visit_time / 1000000 + (strftime('%s', '1601-01-01T00:00:00')) + 32400, 'unixepoch') AS visit_time_KST,
               (visits.visit_duration / 3600 / 1000000) || ' h ' || strftime('%M m %S s', visits.visit_duration / 1000000 / 86400.0) AS visit_duration,
               title,
               urls.url AS url
        FROM urls
        LEFT JOIN visits ON urls.id = visits.url
        ORDER BY visit_time DESC;
    """)
    columns = [desc[0] for desc in cursor.description]
    browsing_history = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Download history
    cursor.execute("""
        SELECT datetime(start_time / 1000000 + (strftime('%s', '1601-01-01T00:00:00')) + 32400, 'unixepoch') AS download_start_KST,
               total_bytes,
               received_bytes,
               mime_type,
               current_path AS path,
               tab_url,
               referrer
        FROM downloads
        ORDER BY start_time DESC;
    """)
    columns = [desc[0] for desc in cursor.description]
    download_history = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return {
        "browsing_history": browsing_history,
        "download_history": download_history
    }


def parse_mozilla(cursor) -> dict:
    # Browsing history
    cursor.execute("""
        SELECT datetime(last_visit_date / 1000000 + (strftime('%s', '1970-01-01T00:00:00')) + 32400, 'unixepoch') AS visit_time_KST,
               title,
               url
        FROM moz_places
        ORDER BY last_visit_date DESC;
    """)
    columns = [desc[0] for desc in cursor.description]
    browsing_history = [dict(zip(columns, row)) for row in cursor.fetchall()]

    # Download history
    cursor.execute("""
        SELECT datetime(dateAdded / 1000000 + (strftime('%s', '1970-01-01T00:00:00')) + 32400, 'unixepoch') AS download_start_KST,
               content
        FROM moz_annos
        ORDER BY dateAdded DESC;
    """)
    columns = [desc[0] for desc in cursor.description]
    download_history = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return {
        "browsing_history": browsing_history,
        "download_history": download_history
    }


def parse_safari(cursor) -> dict:
    # Browsing history only (Safari stores downloads in plist)
    cursor.execute("""
        SELECT datetime(visit_time + (strftime('%s', '2001-01-01T00:00:00')) + 32400, 'unixepoch') AS visit_time_KST,
               title,
               url
        FROM history_visits
        INNER JOIN history_items ON history_items.id = history_visits.history_item
        ORDER BY visit_time DESC;
    """)
    columns = [desc[0] for desc in cursor.description]
    browsing_history = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return {
        "browsing_history": browsing_history,
        "download_history": [],
        "note": "Safari stores download history in 'Downloads.plist', not in SQLite DB"
    }


@mcp.tool()
def parse_history(history_file_path: str) -> str:
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(
            history_file_path,
            isolation_level=None,
            detect_types=sqlite3.PARSE_COLNAMES
        )
        cursor = conn.cursor()

        # Get SQLite version
        cursor.execute("SELECT sqlite_version();")
        sqlite_version = cursor.fetchone()[0]

        # Detect browser type
        browser_type = detect_browser_type(cursor)
        if not browser_type:
            cursor.close()
            conn.close()
            return json.dumps({
                "success": False,
                "error": "Could not determine browser type from database structure"
            }, ensure_ascii=False, indent=2)

        # Parse based on browser type
        if browser_type == "Chromium-based":
            history_data = parse_chromium(cursor)
        elif browser_type == "Mozilla-based":
            history_data = parse_mozilla(cursor)
        elif browser_type == "Safari-based":
            history_data = parse_safari(cursor)

        # Close connection
        cursor.close()
        conn.close()

        # Build response
        response = {
            "success": True,
            "sqlite_version": sqlite_version,
            "browser_type": browser_type,
            "browsing_history": history_data["browsing_history"],
            "download_history": history_data["download_history"],
            "browsing_count": len(history_data["browsing_history"]),
            "download_count": len(history_data["download_history"])
        }

        if "note" in history_data:
            response["note"] = history_data["note"]

        return json.dumps(response, ensure_ascii=False, indent=2)

    except sqlite3.Error as e:
        return json.dumps({
            "success": False,
            "error": f"SQLite error: {str(e)}"
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()