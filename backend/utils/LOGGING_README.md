# Logging Configuration

This document explains how to control the verbosity of console output in the Concordia Simulation Builder.

## Environment Variables

Add these to your `.env` file to control logging behavior:

### `DEBUG_ENABLED` (default: `true`)

Controls general debug messages tagged with `[DEBUG]`.

```bash
# Enable DEBUG messages (default)
DEBUG_ENABLED=true

# Disable DEBUG messages (quieter console output)
DEBUG_ENABLED=false
```

### `LLM_LOGGING_ENABLED` (default: `true`)

Controls LLM-specific debug messages tagged with `[LLM]`.

```bash
# Enable LLM logging (default)
LLM_LOGGING_ENABLED=true

# Disable LLM logging (hides API call details, response times, errors)
LLM_LOGGING_ENABLED=false
```

## Usage Examples

### Quiet Mode (Minimal Output)

```bash
# In your .env file
DEBUG_ENABLED=false
LLM_LOGGING_ENABLED=false
```

This will suppress most console output, showing only critical errors and simulation progress messages.

### Debug Mode (Verbose Output - Default)

```bash
# In your .env file
DEBUG_ENABLED=true
LLM_LOGGING_ENABLED=true
```

This shows all debug messages including:
- Configuration details
- LLM API calls and response times
- Component initialization
- Simulation progress

### Selective Logging

```bash
# Show general debug but hide LLM details
DEBUG_ENABLED=true
LLM_LOGGING_ENABLED=false
```

This shows configuration and simulation progress but hides verbose LLM API details.

## Programmatic Control

You can also control logging at runtime:

```python
from backend.utils.logger import set_debug_enabled, set_llm_logging_enabled

# Disable debug messages programmatically
set_debug_enabled(False)

# Disable LLM logging programmatically
set_llm_logging_enabled(False)

# Check current settings
from backend.utils.logger import is_debug_enabled, is_llm_logging_enabled
print(f"Debug enabled: {is_debug_enabled()}")
print(f"LLM logging enabled: {is_llm_logging_enabled()}")
```

## Using the Logger in Code

```python
from backend.utils.logger import debug_print

# Print DEBUG message (respects DEBUG_ENABLED)
debug_print("This is a debug message", "DEBUG")

# Print LLM message (respects LLM_LOGGING_ENABLED)
debug_print("API call to OpenAI", "LLM")

# Print custom category message
debug_print("Custom info", "INFO")
```

## Impact on Different Message Types

| Setting | Messages Affected |
|---------|-------------------|
| `DEBUG_ENABLED=false` | `[DEBUG]` configuration details, component initialization, variable extraction |
| `LLM_LOGGING_ENABLED=false` | `[LLM]` API calls, response times, timeouts, retries, model info |
| Both `false` | Only critical errors and simulation progress (✓ Completed, Step X/Y) shown |

## Notes

- These settings only affect **console output**, not log files
- Simulation results are always saved to `logs/` directory regardless of logging settings
- Critical errors are always shown even when debug logging is disabled
