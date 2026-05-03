# Timeout Configuration Guide

This guide explains all timeout-related configuration parameters in the Concordia Simulation Builder.

## Overview

The system has **4 layers of timeout protection** to handle long-running simulations while preventing indefinite hangs:

1. **Per-LLM-request timeout** - Maximum time for a single LLM API call
2. **Retry logic** - How to handle transient failures
3. **Watchdog monitoring** - Detects when simulation stops making progress
4. **Frontend timeout** - How long the web UI waits for completion

## Key Principle

**All timeouts wait the FULL duration before flagging an error.**

The system does NOT prematurely interrupt long-running requests. If a timeout is set to 180 seconds:
- Request completes at 179s → **SUCCESS** ✓
- Request completes at 181s → **TIMEOUT** ✗ (then retry)

---

## Configuration Parameters

### 1. LLM_TIMEOUT (Per-Request Timeout)

**Environment Variable:** `LLM_TIMEOUT`
**Default:** `180` (3 minutes)
**Unit:** Seconds

**What it controls:** Maximum time to wait for a **single LLM API call** to complete.

**When to adjust:**
- **Increase** if using slow models or very large prompts
- **Decrease** to detect hangs sooner (but may cause false timeouts)

**Typical values:**
- Fast models (DeepSeek): `60-120` (1-2 minutes)
- Standard models (GPT-4, Claude): `120-180` (2-3 minutes)
- Slow models (Ollama): `180-300` (3-5 minutes)

**Example:**
```bash
# For very slow models
LLM_TIMEOUT=300
```

---

### 2. LLM_REASONING_TIMEOUT (Reasoning Models Only)

**Environment Variable:** `LLM_REASONING_TIMEOUT`
**Default:** `300` (5 minutes)
**Unit:** Seconds

**What it controls:** Maximum time for reasoning models (O1, O3, GPT-5) which perform internal reasoning.

**When to use:** Only applies to models starting with `o1-`, `o3-`, `gpt-5`. Falls back to `LLM_TIMEOUT` if not set.

**Typical values:**
- O3-mini: `180-300` (3-5 minutes)
- O1-preview: `300-600` (5-10 minutes)
- GPT-5: `300-600` (5-10 minutes)

**Example:**
```bash
# For O3-mini on complex prompts
LLM_REASONING_TIMEOUT=300
```

---

### 3. LLM_MAX_RETRIES (Retry Attempts)

**Environment Variable:** `LLM_MAX_RETRIES`
**Default:** `2`
**Unit:** Count (integer)

**What it controls:** Number of times to retry a failed LLM call before giving up.

**Retry schedule:**
- Retry 1: Wait 3 seconds, then retry
- Retry 2: Wait 6 seconds, then retry

**Worst-case time per LLM call:**
```
Total = (timeout × (retries + 1)) + wait_time
Example: (180s × 3) + 9s = 549s (~9 minutes)
```

**When to adjust:**
- **Increase** for unreliable networks (e.g., `3` retries)
- **Decrease** to fail faster (e.g., `1` retry)

**Example:**
```bash
# For unreliable network connections
LLM_MAX_RETRIES=3
```

---

### 4. WATCHDOG_TIMEOUT_SECONDS (Step Progress Monitoring)

**Environment Variable:** `WATCHDOG_TIMEOUT_SECONDS`
**Default:** `600` (10 minutes)
**Unit:** Seconds

**What it controls:** Maximum time to wait without **any step completing** before logging a warning.

**What is a "step"?**
- All agents have acted once
- With 6 agents, one step = 6 LLM calls

**Important:** This does **NOT** kill the simulation - it only logs a warning for monitoring.

**When to adjust:**
- **Increase** if using many agents (6+) or very slow models
- **Decrease** to detect hangs sooner (but may cause false warnings)

**Calculation:**
```
Recommended = (agents × avg_LLM_time) × safety_margin
Example: (6 agents × 60s) × 2 = 720s (12 minutes)
```

**Example:**
```bash
# For 10 agents with slow model
WATCHDOG_TIMEOUT_SECONDS=1200
```

---

### 5. VITE_SIMULATION_TIMEOUT (Frontend Timeout)

**Environment Variable:** `VITE_SIMULATION_TIMEOUT`
**Default:** `18000000` (5 hours)
**Unit:** Milliseconds

**What it controls:** How long the web UI waits for the backend to complete the simulation.

**Important:**
- The backend **continues running** even if frontend times out
- Results are saved to `logs/` directory regardless
- This only affects the web browser connection

**When to adjust:**
- **Increase** for very long simulations
- Frontend timeout calculation:

```
VITE_SIMULATION_TIMEOUT = (steps × agents × avg_LLM_time) × safety_margin

Example: 30 steps × 6 agents × 60s × 2 = 21600s = 21600000ms (6 hours)
```

**Example:**
```bash
# For 6-hour simulation
VITE_SIMULATION_TIMEOUT=21600000
```

---

## Configuration Examples

### Fast Models (DeepSeek, Small Simulations)

```bash
# Quick simulations with fast models
LLM_TIMEOUT=60
LLM_MAX_RETRIES=2
WATCHDOG_TIMEOUT_SECONDS=300
VITE_SIMULATION_TIMEOUT=3600000  # 1 hour
```

### Standard Models (GPT-4, Claude, Medium Simulations)

```bash
# Default configuration (recommended for most users)
LLM_TIMEOUT=180
LLM_MAX_RETRIES=2
WATCHDOG_TIMEOUT_SECONDS=600
VITE_SIMULATION_TIMEOUT=18000000  # 5 hours
```

### Reasoning Models (O3, GPT-5, Complex Simulations)

```bash
# Slow reasoning models with complex prompts
LLM_REASONING_TIMEOUT=600
LLM_MAX_RETRIES=3
WATCHDOG_TIMEOUT_SECONDS=1200
VITE_SIMULATION_TIMEOUT=21600000  # 6 hours
```

### Many Agents (10+ agents, Long Simulations)

```bash
# Large-scale simulations with many agents
LLM_TIMEOUT=180
LLM_MAX_RETRIES=2
WATCHDOG_TIMEOUT_SECONDS=1800
VITE_SIMULATION_TIMEOUT=43200000  # 12 hours
```

---

## Troubleshooting

### Problem: Frequent Timeouts

**Symptoms:** Logs show `[LLM] Timeout after X.Xs` errors

**Solutions:**
1. **Increase `LLM_TIMEOUT`** - Current value may be too short for your model
2. **Increase `LLM_MAX_RETRIES`** - Allow more recovery attempts
3. **Check model responsiveness** - API may be overloaded
4. **Try a different provider** - Switch to a faster model

### Problem: Watchdog Warnings

**Symptoms:** Logs show `[WATCHDOG] No progress for Xs` but simulation continues

**Solutions:**
1. **Increase `WATCHDOG_TIMEOUT_SECONDS`** - Allow more time per step
2. **Reduce simulation complexity** - Fewer agents or steps
3. **Use a faster model** - Reduce per-LLM-call time

### Problem: Frontend Timeout

**Symptoms:** Browser shows timeout error, but backend is still running

**Solutions:**
1. **Increase `VITE_SIMULATION_TIMEOUT`** - Allow more time
2. **Check logs directory** - Results will be saved there
3. **Run smaller simulations** - Break into smaller chunks

### Problem: Simulation Takes Too Long

**Symptoms:** Simulation completes but takes hours

**Solutions:**
1. **Use faster model** - DeepSeek instead of O3/GPT-5
2. **Reduce agents** - 3-4 agents instead of 6+
3. **Reduce steps** - 10-15 steps instead of 30+
4. **Simplify game master** - Use `generic` instead of `game_theoretic`

---

## Formula Summary

### Per-LLM-Call Maximum Time
```
max_time_per_call = LLM_TIMEOUT × (LLM_MAX_RETRIES + 1) + retry_wait_time

Example: 180s × 3 + 9s = 549s (~9 minutes)
```

### Per-Step Maximum Time
```
max_time_per_step = max_time_per_call × num_agents

Example: 549s × 6 agents = 3294s (~55 minutes)
```

### Total Simulation Maximum Time
```
max_simulation_time = max_time_per_step × num_steps

Example: 3294s × 30 steps = 98820s (~27 hours)
```

### Frontend Timeout Recommendation
```
VITE_SIMULATION_TIMEOUT = max_simulation_time × 1.5 (safety margin)

Example: 98820s × 1.5 = 148230s = 148230000ms (~41 hours)
```

---

## Files to Modify

To configure timeouts, edit these files:

1. **Root `.env`** - Backend configuration (recommended)
   ```bash
   LLM_TIMEOUT=180
   LLM_REASONING_TIMEOUT=300
   LLM_MAX_RETRIES=2
   WATCHDOG_TIMEOUT_SECONDS=600
   ```

2. **`frontend/.env`** - Frontend configuration
   ```bash
   VITE_SIMULATION_TIMEOUT=18000000  # 5 hours
   ```

**Note:** Always copy values from `.env.example` to your actual `.env` file to apply changes.
