# Browser DB Parser MCP Server

Web History 파일을 파싱하여 JSON으로 반환하는 MCP Server

## 설치

```bash
pip install -r requirements.txt
```

## Claude Desktop 설정

`claude_desktop_config.json`에 추가:

```json
{
  "mcpServers": {
    "browser-db-parser": {
      "command": "python",
      "args": ["C:\\Users\\home\\Desktop\\Made_Tools\\BrowerDBParser_MCP\\server.py"]
    }
  }
}
```

## 도구

### get_info

MCP 서버 정보를 반환합니다.

**파라미터:** None

**반환값 (JSON):**
```json
{
  "name": "browser-db-parser",
  "version": "1.0.0",
  "description": "Browser history database parser MCP server...",
  "supported_browsers": ["Chromium-based", "Mozilla-based", "Safari-based"],
  "tools": [...]
}
```

### parse_history

브라우저 히스토리 SQLite DB 파일을 파싱합니다.

**파라미터:**
- `history_file_path`: History 파일의 절대 경로

**반환값 (JSON):**
```json
{
  "success": true,
  "sqlite_version": "3.x.x",
  "browser_type": "Chromium-based",
  "browsing_history": [...],
  "download_history": [...],
  "browsing_count": 100,
  "download_count": 10
}
```
