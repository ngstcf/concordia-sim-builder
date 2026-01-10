# Diagnostic and Error Handling Improvements

This document describes improvements made to help diagnose simulation issues and prevent data loss.

## Recent Improvements (Jan 10, 2025)

### 1. Enhanced Checkpoint System
- **Fixed**: Checkpoints now save actual HTML content instead of Python object representation
- **Method**: Uses `PythonObjectToHTMLConverter(sim.get_raw_log())` to convert raw simulation data to HTML
- **Benefit**: Checkpoint files now grow in size and contain actual simulation state

### 2. Emergency Checkpoint on Completion
- **Location**: After simulation completes, before HTML processing
- **Filename**: `{timestamp}_EMERGENCY_CHECKPOINT.html`
- **Purpose**: Ensures data is saved even if subsequent HTML processing fails
- **Benefit**: Prevents total data loss if post-processing crashes

### 3. Watchdog Emergency Saves
- **Trigger**: When no progress for `WATCHDOG_TIMEOUT_SECONDS` (default: 10 minutes)
- **Filename**: `{timestamp}_WATCHDOG_EMERGENCY_step{N}.html`
- **Purpose**: Saves partial simulation if it hangs during execution
- **Benefit**: Recovers data from hung simulations

### 4. Enhanced Logging

#### Heartbeat Logging
- **When**: Every time a step completes
- **Format**: `[HEARTBEAT] {timestamp} - Step {N}/{max} callback received`
- **Purpose**: Track exact timing of step completions
- **Benefit**: Easy to spot where simulation stopped progressing

#### Watchdog Periodic Status
- **When**: Every minute during no-progress periods
- **Format**: `[WATCHDOG] {timestamp} - No progress for {X}s, last step: {N}/{max}`
- **Purpose**: Continuous monitoring during hangs
- **Benefit**: Know simulation is still running but stuck

#### Detailed Error Messages
- Error type and full traceback on simulation failures
- Raw log entry count when extracting partial results
- Results type and length for debugging

### 5. Debug Messages Added

| Location | Message | Purpose |
|----------|---------|---------|
| Pre-results | `Waiting for future.result() to get simulation results...` | Know when waiting for completion |
| Post-results | `Simulation completed successfully, got results (type: {type})` | Confirm completion and type |
| Post-results | `Results length: {N} characters` | Verify data size |
| Partial save | `Retrieved raw_log with {N} entries` | Confirm partial data extraction |
| Partial save | `Saved partial results due to simulation error ({N} chars)` | Confirm partial save |

## Checkpoint File Types

| Type | Filename Pattern | When Created | Content |
|------|------------------|--------------|---------|
| Regular | `*_checkpoint_step{N}.html` | Every 5 steps during execution | Partial simulation up to step N |
| Emergency | `*_EMERGENCY_CHECKPOINT.html` | After simulation completes | Full simulation results (backup) |
| Watchdog | `*_WATCHDOG_EMERGENCY_step{N}.html` | When hung for >10 min | Partial simulation up to last step |
| Final | `{timestamp}_{agents}_{premise}.html` | On successful completion | Full simulation with all processing |

## Troubleshooting Guide

### Simulation stopped at step N, no file saved

**Check logs for:**
1. `[HEARTBEAT]` messages - last one shows last completed step
2. `[WATCHDOG]` messages - shows when it detected the hang
3. `[WATCHDOG] ✓ Emergency checkpoint saved` - confirms partial save

**Recovery:**
- Look for `{timestamp}_WATCHDOG_EMERGENCY_step{N}.html` in `logs/`
- Contains all data up to the last completed step

### Simulation running but no progress updates

**Check logs for:**
1. `[WATCHDOG] {timestamp} - No progress for {X}s` - confirms watchdog detected it
2. Last `[HEARTBEAT]` - shows last successful step

**Action:**
- Wait for watchdog emergency save (after 10 min of no progress)
- Or kill and use the checkpoint

### Results file is empty/corrupted

**Check logs for:**
1. `[CHECKPOINT] ✓ Emergency checkpoint saved` - you have a backup
2. Look for `*_EMERGENCY_CHECKPOINT.html` in `logs/`

**Recovery:**
- Use the emergency checkpoint file instead of the main file

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `WATCHDOG_ENABLED` | `true` | Enable/disable watchdog monitoring |
| `WATCHDOG_TIMEOUT_SECONDS` | `600` | Seconds of no progress before emergency save |
| `LLM_TIMEOUT` | `250` | LLM API call timeout in seconds |
| `LLM_MAX_RETRIES` | `2` | Number of retries on LLM timeout |

## Log Message Quick Reference

| Prefix | Meaning |
|--------|---------|
| `[HEARTBEAT]` | Step completed successfully |
| `[WATCHDOG]` | Monitoring for hangs |
| `[CHECKPOINT]` | Saving checkpoint file |
| `[DEBUG]` | Diagnostic information |
| `[ERROR]` | Simulation failed |
| `[WARNING]` | Non-fatal issue |
| `[LLM]` | LLM API call |
| `[SSE]` | Server-Sent Events to frontend |

