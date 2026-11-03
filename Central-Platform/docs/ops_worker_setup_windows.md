# Ops Worker Setup (Windows)

This project includes notification retry processing.

## Option A: Long-running worker (interactive/session service)

Run:
```powershell
.\scripts\run_ops_worker.ps1 -IntervalSeconds 30 -Limit 100
```

This keeps a loop alive and processes pending notifications repeatedly.

## Option B: Windows Task Scheduler (recommended baseline)

Registers a task that runs every minute:
```powershell
.\scripts\register_notifications_task.ps1
```

Runner script used by the task:
```powershell
.\scripts\run_notifications_once.ps1
```

## Manual commands

Single pass:
```powershell
.\.venv\Scripts\python.exe manage.py process_notifications --limit 100
```

Loop mode:
```powershell
.\.venv\Scripts\python.exe manage.py run_ops_worker --interval 30 --limit 100
```

## Notes
- Failed events are retried until `max_attempts`.
- Retry schedule is based on `next_attempt_at`.
- Configure email/webhook/SMS in `.env`.
