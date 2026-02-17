# ArenaAgent - Database Schema (JSON Files)

## JSON Storage Schema Definitions

---

## OVERVIEW

ArenaAgent uses JSON files for data persistence. All data is stored locally in `~/.arenaagent/`.

### Storage Structure:
```
~/.arenaagent/
├── config.json                          # Global configuration
├── browser/                             # Playwright browser profile
│   └── [chromium profile files]
└── sessions/
    ├── {session_id_1}/
    │   ├── metadata.json                # Session metadata
    │   ├── conversation_history.json    # Messages
    │   ├── file_index.json              # Files created/modified
    │   └── execution_log.json           # Execution results
    ├── {session_id_2}/
    │   └── ...
    └── .archive/                        # Archived/corrupted sessions
        └── {session_id}/
            └── ...
```

---

## 1. CONFIG.JSON SCHEMA

### Location: `~/.arenaagent/config.json`

### Purpose:
Global application configuration, persists across sessions.

### Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version"],
  "properties": {
    "version": {
      "type": "string",
      "description": "Config schema version",
      "pattern": "^\\d+\\.\\d+$",
      "example": "1.0"
    },
    "default_model": {
      "type": "string",
      "description": "Default LLM model to use",
      "default": "claude-3.5-sonnet",
      "enum": [
        "claude-3.5-sonnet",
        "gpt-4",
        "gpt-4-turbo",
        "gemini-pro"
      ]
    },
    "default_workspace": {
      "type": "string",
      "description": "Default workspace directory",
      "default": "~/arenaagent_workspace/"
    },
    "browser": {
      "type": "object",
      "properties": {
        "profile_path": {
          "type": "string",
          "description": "Browser profile directory",
          "default": "~/.arenaagent/browser/"
        },
        "headless": {
          "type": "boolean",
          "description": "Run browser in headless mode",
          "default": true
        },
        "timeout": {
          "type": "integer",
          "description": "Browser operation timeout (seconds)",
          "default": 30,
          "minimum": 10,
          "maximum": 300
        }
      }
    },
    "execution": {
      "type": "object",
      "properties": {
        "auto_approve": {
          "type": "boolean",
          "description": "Auto-approve code execution without prompting",
          "default": false
        },
        "timeout": {
          "type": "integer",
          "description": "Code execution timeout (seconds)",
          "default": 60,
          "minimum": 10,
          "maximum": 600
        },
        "max_retries": {
          "type": "integer",
          "description": "Max retry attempts for error recovery",
          "default": 3,
          "minimum": 1,
          "maximum": 5
        }
      }
    },
    "files": {
      "type": "object",
      "properties": {
        "auto_backup": {
          "type": "boolean",
          "description": "Automatically backup before file modifications",
          "default": true
        },
        "backup_retention_days": {
          "type": "integer",
          "description": "Days to keep backups before cleanup",
          "default": 30,
          "minimum": 1
        }
      }
    },
    "session": {
      "type": "object",
      "properties": {
        "auto_save": {
          "type": "boolean",
          "description": "Automatically save messages",
          "default": true
        },
        "context_window_tokens": {
          "type": "integer",
          "description": "Maximum context tokens to send to model",
          "default": 50000,
          "minimum": 1000
        }
      }
    }
  }
}
```

### Example:

```json
{
  "version": "1.0",
  "default_model": "claude-3.5-sonnet",
  "default_workspace": "~/arenaagent_workspace/",
  "browser": {
    "profile_path": "~/.arenaagent/browser/",
    "headless": true,
    "timeout": 30
  },
  "execution": {
    "auto_approve": false,
    "timeout": 60,
    "max_retries": 3
  },
  "files": {
    "auto_backup": true,
    "backup_retention_days": 30
  },
  "session": {
    "auto_save": true,
    "context_window_tokens": 50000
  }
}
```

---

## 2. METADATA.JSON SCHEMA

### Location: `~/.arenaagent/sessions/{session_id}/metadata.json`

### Purpose:
Session metadata, created when session starts, updated on each interaction.

### Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["session_id", "created_at", "model", "workspace"],
  "properties": {
    "session_id": {
      "type": "string",
      "description": "UUID v4 session identifier",
      "pattern": "^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
      "example": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of session creation",
      "example": "2026-02-17T10:30:00Z"
    },
    "last_updated": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of last activity",
      "example": "2026-02-17T15:45:30Z"
    },
    "model": {
      "type": "string",
      "description": "LLM model used in this session",
      "example": "claude-3.5-sonnet"
    },
    "workspace": {
      "type": "string",
      "description": "Workspace directory for this session",
      "example": "/home/user/arenaagent_workspace/"
    },
    "message_count": {
      "type": "integer",
      "description": "Total messages in conversation",
      "minimum": 0,
      "example": 24
    },
    "total_tokens_estimated": {
      "type": "integer",
      "description": "Estimated total tokens used",
      "minimum": 0,
      "example": 45000
    },
    "files_created_count": {
      "type": "integer",
      "description": "Number of files created in this session",
      "minimum": 0,
      "example": 5
    },
    "executions_count": {
      "type": "integer",
      "description": "Number of code executions",
      "minimum": 0,
      "example": 12
    }
  }
}
```

### Example:

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created_at": "2026-02-17T10:30:00Z",
  "last_updated": "2026-02-17T15:45:30Z",
  "model": "claude-3.5-sonnet",
  "workspace": "/home/user/arenaagent_workspace/",
  "message_count": 24,
  "total_tokens_estimated": 45000,
  "files_created_count": 5,
  "executions_count": 12
}
```

---

## 3. CONVERSATION_HISTORY.JSON SCHEMA

### Location: `~/.arenaagent/sessions/{session_id}/conversation_history.json`

### Purpose:
Complete conversation history, appended after each user/assistant exchange.

### Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["session_id", "messages"],
  "properties": {
    "session_id": {
      "type": "string",
      "description": "UUID v4 session identifier"
    },
    "messages": {
      "type": "array",
      "description": "Ordered list of conversation messages",
      "items": {
        "type": "object",
        "required": ["id", "timestamp", "role", "content"],
        "properties": {
          "id": {
            "type": "integer",
            "description": "Sequential message ID within session",
            "minimum": 1
          },
          "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 timestamp"
          },
          "role": {
            "type": "string",
            "enum": ["user", "assistant", "system"],
            "description": "Message sender role"
          },
          "content": {
            "type": "string",
            "description": "Message content (plain text)"
          },
          "tokens_estimated": {
            "type": "integer",
            "description": "Estimated token count for this message",
            "minimum": 0
          },
          "metadata": {
            "type": "object",
            "description": "Additional message metadata",
            "properties": {
              "files_created": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files created by this message"
              },
              "files_modified": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Files modified by this message"
              },
              "execution_attempted": {
                "type": "boolean",
                "description": "Whether code execution was attempted"
              },
              "execution_success": {
                "type": "boolean",
                "description": "Whether execution succeeded"
              },
              "retry_count": {
                "type": "integer",
                "description": "Number of retry attempts",
                "minimum": 0
              }
            }
          }
        }
      }
    }
  }
}
```

### Example:

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "messages": [
    {
      "id": 1,
      "timestamp": "2026-02-17T10:30:15Z",
      "role": "user",
      "content": "create a Flask REST API for a todo list",
      "tokens_estimated": 12,
      "metadata": {}
    },
    {
      "id": 2,
      "timestamp": "2026-02-17T10:30:23Z",
      "role": "assistant",
      "content": "I'll create a Flask REST API for a todo list...\n\n```python\nfrom flask import Flask, jsonify, request\n\napp = Flask(__name__)\n\ntodos = []\n\n@app.route('/todos', methods=['GET'])\ndef get_todos():\n    return jsonify(todos)\n\n@app.route('/todos', methods=['POST'])\ndef create_todo():\n    todo = request.json\n    todos.append(todo)\n    return jsonify(todo), 201\n\nif __name__ == '__main__':\n    app.run(debug=True)\n```\n\nSave this as `app.py` and run it.",
      "tokens_estimated": 245,
      "metadata": {
        "files_created": ["app.py"],
        "files_modified": [],
        "execution_attempted": true,
        "execution_success": false,
        "retry_count": 1
      }
    },
    {
      "id": 3,
      "timestamp": "2026-02-17T10:30:30Z",
      "role": "system",
      "content": "Execution error: ModuleNotFoundError: No module named 'flask'",
      "tokens_estimated": 15,
      "metadata": {
        "execution_attempted": true,
        "execution_success": false
      }
    },
    {
      "id": 4,
      "timestamp": "2026-02-17T10:31:05Z",
      "role": "assistant",
      "content": "You need to install Flask first:\n\n```bash\npip install flask\n```\n\nThen run the app again.",
      "tokens_estimated": 32,
      "metadata": {
        "execution_attempted": true,
        "execution_success": true,
        "retry_count": 0
      }
    }
  ]
}
```

---

## 4. FILE_INDEX.JSON SCHEMA

### Location: `~/.arenaagent/sessions/{session_id}/file_index.json`

### Purpose:
Track all files created/modified during session, with backup information.

### Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["session_id", "files"],
  "properties": {
    "session_id": {
      "type": "string",
      "description": "UUID v4 session identifier"
    },
    "files": {
      "type": "array",
      "description": "List of files created/modified",
      "items": {
        "type": "object",
        "required": ["path", "created_at"],
        "properties": {
          "path": {
            "type": "string",
            "description": "Absolute file path"
          },
          "created_at": {
            "type": "string",
            "format": "date-time",
            "description": "When file was first created by agent"
          },
          "last_modified": {
            "type": "string",
            "format": "date-time",
            "description": "Last modification by agent"
          },
          "size_bytes": {
            "type": "integer",
            "description": "Current file size in bytes",
            "minimum": 0
          },
          "hash_sha256": {
            "type": "string",
            "description": "SHA256 hash of current content",
            "pattern": "^[a-f0-9]{64}$"
          },
          "language": {
            "type": "string",
            "description": "Detected programming language",
            "example": "python"
          },
          "backups": {
            "type": "array",
            "description": "List of backup files",
            "items": {
              "type": "object",
              "properties": {
                "path": {
                  "type": "string",
                  "description": "Backup file path"
                },
                "timestamp": {
                  "type": "integer",
                  "description": "Unix timestamp of backup"
                },
                "size_bytes": {
                  "type": "integer",
                  "description": "Backup file size"
                }
              }
            }
          },
          "modification_count": {
            "type": "integer",
            "description": "Number of times file was modified",
            "minimum": 0
          }
        }
      }
    }
  }
}
```

### Example:

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "files": [
    {
      "path": "/home/user/arenaagent_workspace/app.py",
      "created_at": "2026-02-17T10:30:25Z",
      "last_modified": "2026-02-17T15:45:12Z",
      "size_bytes": 1243,
      "hash_sha256": "abc123def456...",
      "language": "python",
      "backups": [
        {
          "path": "/home/user/arenaagent_workspace/app.py.backup.1707300025",
          "timestamp": 1707300025,
          "size_bytes": 892
        },
        {
          "path": "/home/user/arenaagent_workspace/app.py.backup.1707303312",
          "timestamp": 1707303312,
          "size_bytes": 1105
        }
      ],
      "modification_count": 2
    },
    {
      "path": "/home/user/arenaagent_workspace/requirements.txt",
      "created_at": "2026-02-17T11:20:00Z",
      "last_modified": "2026-02-17T11:20:00Z",
      "size_bytes": 45,
      "hash_sha256": "def789abc012...",
      "language": "text",
      "backups": [],
      "modification_count": 0
    }
  ]
}
```

---

## 5. EXECUTION_LOG.JSON SCHEMA

### Location: `~/.arenaagent/sessions/{session_id}/execution_log.json`

### Purpose:
Log of all code executions, outcomes, and errors.

### Schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["session_id", "executions"],
  "properties": {
    "session_id": {
      "type": "string",
      "description": "UUID v4 session identifier"
    },
    "executions": {
      "type": "array",
      "description": "List of code executions",
      "items": {
        "type": "object",
        "required": ["id", "timestamp", "language", "command", "exit_code"],
        "properties": {
          "id": {
            "type": "integer",
            "description": "Sequential execution ID"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "When execution occurred"
          },
          "language": {
            "type": "string",
            "enum": ["python", "bash", "sh", "node"],
            "description": "Language/runtime used"
          },
          "command": {
            "type": "string",
            "description": "Actual command executed"
          },
          "code": {
            "type": "string",
            "description": "Code that was executed (if inline)"
          },
          "file_executed": {
            "type": "string",
            "description": "File path if executing a file"
          },
          "exit_code": {
            "type": "integer",
            "description": "Process exit code (0 = success)"
          },
          "stdout": {
            "type": "string",
            "description": "Standard output captured"
          },
          "stderr": {
            "type": "string",
            "description": "Standard error captured"
          },
          "duration_ms": {
            "type": "integer",
            "description": "Execution duration in milliseconds",
            "minimum": 0
          },
          "timed_out": {
            "type": "boolean",
            "description": "Whether execution was killed due to timeout"
          },
          "retry_attempt": {
            "type": "integer",
            "description": "Retry attempt number (0 = first try)",
            "minimum": 0
          },
          "error_type": {
            "type": "string",
            "description": "Classified error type if failed",
            "enum": [
              "missing_module",
              "syntax_error",
              "runtime_error",
              "timeout",
              "permission_denied",
              "command_not_found"
            ]
          }
        }
      }
    }
  }
}
```

### Example:

```json
{
  "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "executions": [
    {
      "id": 1,
      "timestamp": "2026-02-17T10:30:30Z",
      "language": "python",
      "command": "python app.py",
      "code": null,
      "file_executed": "/home/user/arenaagent_workspace/app.py",
      "exit_code": 1,
      "stdout": "",
      "stderr": "ModuleNotFoundError: No module named 'flask'\n",
      "duration_ms": 145,
      "timed_out": false,
      "retry_attempt": 0,
      "error_type": "missing_module"
    },
    {
      "id": 2,
      "timestamp": "2026-02-17T10:31:15Z",
      "language": "bash",
      "command": "pip install flask",
      "code": "pip install flask",
      "file_executed": null,
      "exit_code": 0,
      "stdout": "Successfully installed flask-3.0.0\n",
      "stderr": "",
      "duration_ms": 3421,
      "timed_out": false,
      "retry_attempt": 0,
      "error_type": null
    },
    {
      "id": 3,
      "timestamp": "2026-02-17T10:31:20Z",
      "language": "python",
      "command": "python app.py",
      "code": null,
      "file_executed": "/home/user/arenaagent_workspace/app.py",
      "exit_code": 0,
      "stdout": " * Running on http://127.0.0.1:5000\n * Debug mode: on\n",
      "stderr": "",
      "duration_ms": null,
      "timed_out": false,
      "retry_attempt": 1,
      "error_type": null
    }
  ]
}
```

---

## DATA INTEGRITY GUARANTEES

### Atomic Writes:
All JSON writes use atomic operations:
1. Write to temp file: `{file}.tmp.{random}`
2. Flush to disk: `fsync()`
3. Atomic rename: `os.replace()`

**Result:** Never partial/corrupted JSON files

### Backup Strategy:
Before overwriting any JSON file:
1. Create backup: `{file}.backup.{timestamp}`
2. Keep last 5 backups
3. Auto-delete backups older than 30 days

### Corruption Recovery:
If JSON file is corrupted:
1. Detect: JSON parse error
2. Archive: Move to `sessions/.archive/{session_id}/`
3. Fallback: Create new session with warning

---

## QUERY PATTERNS

### Load Recent Sessions:
```python
# Read all metadata.json files
# Sort by last_updated
# Return top N
```

### Get Context for Prompt:
```python
# Read conversation_history.json
# Filter last N messages
# Estimate tokens
# Truncate if exceeds limit
```

### Find File Backups:
```python
# Read file_index.json
# Find file entry
# Return backups array
# Sort by timestamp descending
```

### Calculate Session Stats:
```python
# Read metadata.json
# Read execution_log.json
# Count successes vs failures
# Calculate total duration
```

---

## MIGRATION STRATEGY

### Version 1.0 → 1.1:
If schema changes in future:
1. Add `schema_version` field to each JSON
2. Migration script: `arenaagent migrate`
3. Backward compatible reads (defaults for new fields)

---

*Schema definitions complete. See API_SPECIFICATION.md for usage in code.*