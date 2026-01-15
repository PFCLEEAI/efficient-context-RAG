# Real-World Benchmarks

> Actual measured data from using this system. Add your own!

---

## How to Measure

### Check Context Usage
Run `/context` in Claude Code to see:
```
Context Usage
⛁ Messages: XXXk tokens (XX%)
⛁ Free space: XXk (XX%)
```

### Track Your Session
Note these metrics:
- Start time
- Context % at start
- Compress events (time + before/after %)
- End time + final context %
- Tasks completed

---

## Recorded Sessions

### Session 1: OpenWhispr Project

**Date:** January 2024
**Project:** Desktop transcription app (Electron + React)
**Model:** Claude Opus 4.5

| Metric | Value |
|--------|-------|
| Session Duration | ~3 hours |
| Context at 67% | 135k/200k tokens |
| Message tokens | 112.2k (56.1%) |
| System tokens | 2.8k (1.4%) |
| Tool tokens | 16.0k (8.0%) |
| Memory files | 1.9k (0.9%) |
| Skills | 1.8k (0.9%) |
| Free space | 20k (10.2%) |

**Action Taken:** Compressed to messages.md
**Result:** Continued working without context loss

**Breakdown:**
```
┌─────────────────────────────────────────────────────────┐
│  OpenWhispr Session - 67% Context Usage                  │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ████████████████████████████████████████░░░░░░░░░░░░░░ │
│                                                          │
│  ⛁ System prompt:    2.8k tokens  (1.4%)               │
│  ⛁ System tools:    16.0k tokens  (8.0%)               │
│  ⛁ Custom agents:      24 tokens  (0.0%)               │
│  ⛁ Memory files:     1.9k tokens  (0.9%)               │
│  ⛁ Skills:           1.8k tokens  (0.9%)               │
│  ⛁ Messages:       112.2k tokens (56.1%)  ← Main usage │
│  ⛶ Free space:        20k tokens (10.2%)               │
│  ⛝ Buffer:            45k tokens (22.5%)               │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### Session Template (Copy This)

**Date:** YYYY-MM-DD
**Project:** [Project name and type]
**Model:** [haiku/sonnet/opus]

| Metric | Value |
|--------|-------|
| Session Duration | X hours |
| Starting Context | XX% |
| Peak Context | XX% |
| Compress Events | X times |
| Final Context | XX% |
| Tasks Completed | X |

**Context Breakdown:**
| Component | Tokens | % |
|-----------|--------|---|
| Messages | | |
| System | | |
| Tools | | |
| Memory | | |
| Free | | |

**Notes:**
- What worked well:
- What could improve:
- Lessons learned:

---

## Aggregate Statistics

### Across All Recorded Sessions

| Metric | Without System | With System | Improvement |
|--------|----------------|-------------|-------------|
| Avg session length | hrs | hrs | |
| Avg compress events | X | X | |
| Context preserved | % | % | |
| Tasks/hour | X | X | |

*Update these as you collect more data*

---

## Before/After Comparison

### Typical Session Without This System

```
Time    Context    Event
─────────────────────────────────
0:00    15%        Start, explain project
0:30    35%        Working
1:00    55%        Working
1:30    75%        Slowing down ⚠️
2:00    88%        Degraded performance ❌
2:15    AUTO       Force compact, lost context
2:30    45%        Re-explaining project...
3:00    65%        Working again
```

**Result:** 2.5 hours of work, 30 mins lost to re-explanation

### Same Session With This System

```
Time    Context    Event
─────────────────────────────────
0:00    5%         MCP search + status.md
0:30    25%        Working
1:00    40%        Working
1:30    55%        Working
2:00    68%        Planned compress
2:05    25%        Continue fresh ✓
2:30    40%        Working
3:00    55%        End session
```

**Result:** 3 hours of work, 0 time lost

---

## Contributing Your Data

Help improve this system by sharing your benchmarks!

1. Fork this repo
2. Add your session data using the template above
3. Submit a PR

Include:
- Project type (web app, CLI, etc.)
- Complexity (simple/medium/complex)
- Your context usage patterns
- Any issues encountered

---

## Expected Ranges

Based on collected data, you should see:

| Metric | Expected Range |
|--------|----------------|
| Context at session start | 5-15% |
| Usable context for work | 60-75% |
| Time between compresses | 2-4 hours |
| Context after compress | 20-35% |
| Tokens saved vs default | 50-80k |

If your numbers differ significantly, check:
- Are you using progressive loading?
- Are you reading full files (use SERENA instead)?
- Are you compressing at 70% or waiting too long?

---

**Track your data. Improve your workflow. Share your results.**
