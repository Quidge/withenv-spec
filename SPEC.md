# withenv Specification v1.0.1

`withenv` is a command-line utility that executes a program with environment variables loaded from a file.

## Synopsis

```
withenv ENVFILE COMMAND [ARGS...]
```

## Description

`withenv` reads environment variable definitions from `ENVFILE`, merges them with the current environment, and executes `COMMAND` with the combined environment. The process is replaced via exec—`withenv` does not remain as a parent process.

**Note:** Reading from stdin is not supported. `ENVFILE` must be a path to a regular file.

## Behavior

### Argument Handling

- The first argument is the path to an environment file
- All subsequent arguments form the command to execute
- All arguments after `ENVFILE` are passed through verbatim to the command
- Only `--help` and `--version` are intercepted when passed as the first argument

### Options

Implementations MUST support `--help` and `--version`, along with their short forms `-h` and `-v`. These are only recognized as the **first argument**; in any other position they are passed through to the command.

#### `--version` / `-v`

Output format: space-delimited fields to stdout.

| Position | Required | Content |
|----------|----------|---------|
| 1st | Yes | Program name (`withenv`) |
| 2nd | Yes | Version string |
| 3rd+ | No | Implementation-defined (build info, etc.) |

Example: `withenv 1.0.0`

The exact version string format is implementation-defined (semver, calver, etc.), but it MUST be a single token with no spaces.

#### `--help` / `-h`

Output MUST include:

1. **Synopsis** — usage pattern showing `ENVFILE COMMAND [ARGS...]`
2. **Description** — one-line explanation of what withenv does
3. **Behavior note** — that arguments after ENVFILE pass through to COMMAND
4. **Options** — description of `--help` and `--version`
5. **Exit codes** — list of exit codes and their meanings

The formatting and presentation style is implementation-defined, following the idioms of the implementing language.

### Environment Merging

- Variables from `ENVFILE` are merged into the current process environment
- File variables **override** existing environment variables with the same name
- Variables not defined in the file retain their original values
- The merged environment is passed to the executed command

### Process Execution

- The command is executed via exec (process replacement)
- `withenv` does not fork; it becomes the executed command
- Exit code is that of the executed command
- Signals are handled by the executed command, not `withenv`

## Environment File Format

The file format follows the common `.env` convention:

### Basic Syntax

```
KEY=value
ANOTHER_KEY=another value
```

### Line Grammar

A valid line matches one of:

```
<blank>        ::= /^\s*$/
<comment>      ::= /^\s*#/
<assignment>   ::= [export] <key> "=" <value>
<key>          ::= [A-Za-z_][A-Za-z0-9_]*
<value>        ::= <quoted> | <unquoted>
<quoted>       ::= "'" <single-quoted-content> "'" | '"' <double-quoted-content> '"'
<unquoted>     ::= .*
```

Lines not matching this grammar are **malformed**. Implementations MUST warn to stderr and skip malformed lines.

### Rules

1. **Comments**: Lines beginning with `#` (optionally preceded by whitespace) are ignored
2. **Empty lines**: Blank lines are ignored
3. **Whitespace**: Leading/trailing whitespace around keys is trimmed; whitespace at the start of unquoted values is preserved
4. **Keys**: Must start with a letter or underscore, followed by letters, digits, or underscores. Unicode letters are permitted but may not be portable to all shells.
5. **Quoting**: Values may be quoted with single (`'`) or double (`"`) quotes
6. **Escape sequences**: Within double quotes, `\n`, `\r`, `\t`, `\\`, `\"`, and `\'` are interpreted. Only these escapes are interpreted; all others remain literal.
7. **Single quotes**: Literal strings, no escape interpretation
8. **Unquoted values**: Trailing whitespace is preserved, inline `#` is part of the value
9. **Export prefix**: `export KEY=value` is equivalent to `KEY=value`
10. **Empty values**: `KEY=` sets an empty string
11. **Multiline**: Double-quoted values may span lines with `\n` or literal newlines
12. **Quote concatenation**: When a quoted value is followed by additional content, the quoted portion and trailing content are concatenated (e.g., `KEY="hello"world` produces `helloworld`). Mixed quote styles are supported.

### Examples

```bash
# Database configuration
DB_HOST=localhost
DB_PORT=5432

# Quoted values
MESSAGE="Hello, World!"
PATH_SINGLE='/usr/local/bin'

# With escapes
GREETING="Hello\nWorld"

# Empty value
EMPTY_VAR=

# Export syntax (equivalent to without export)
export API_KEY=secret123
```

## Error Conditions

| Condition | Exit Code | Behavior |
|-----------|-----------|----------|
| No arguments | 10 | Print usage hint to stderr |
| Missing COMMAND | 10 | Print usage hint to stderr |
| ENVFILE not found | 11 | Print file not found message to stderr |
| ENVFILE not readable | 11 | Print permission error to stderr |
| ENVFILE is a directory | 11 | Print appropriate message to stderr |
| COMMAND not found | 127 | Error from exec |
| COMMAND not executable | 126 | Error from exec |
| Malformed ENVFILE line | — | Warn to stderr, skip line, continue |

## Exit Codes

| Code | Source | Meaning |
|------|--------|---------|
| 0 | Command | Success (or command exited 0) |
| 10 | withenv | Usage error (no arguments, missing command) |
| 11 | withenv | File error (not found, not readable, is directory) |
| 126 | exec | Command not executable |
| 127 | exec | Command not found |
| Other | Command | Pass-through from executed command |

## Design Constraints

- **Minimal**: No configuration, only `--help` and `--version` flags
- **Transparent**: Arguments pass through unmodified
- **Ephemeral**: Process replacement, not supervision
- **Predictable**: File variables always override environment
- **Compatible**: Standard .env format used by docker-compose, direnv, etc.

## Non-Goals

- Variable interpolation (`${VAR}` expansion)
- Sourcing multiple files
- Watching files for changes
- Acting as a process supervisor
