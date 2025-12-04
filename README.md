# Browser DB Parser MCP Server

Web HISTORY 파일을 파싱하여 JSON으로 반환하는 MCP Server

## 폴더 위치

이 MCP 서버는 반드시 `C:\Users\home\Desktop\Made_Tools\BrowserDBParser` 도구와 **같은 레벨의 경로**에 위치해야 합니다.

```
C:\Users\home\Desktop\Made_Tools\
├── BrowserDBParser\        ← Amier-ge/BrowserDBParser Tool
└── BrowerDBParser_MCP\     ← MCP Server
```

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
      "args": ["C:\\Users\\home\\Desktop\\Made_Tools\\BrowerDBParser_MCP\\server.py"],
      "env": {
        "PYTHONPATH": "C:\\Users\\home\\Desktop\\Made_Tools\\BrowerDBParser_MCP"
      }
    }
  }
}
```

## 제공 도구

| 도구 | 설명 |
|------|------|
| `parse_history` | 브라우저 히스토리 SQLite DB 파일을 파싱 |
| `get_info` | 도구 정보 조회 |

## 작성자

Amier-ge