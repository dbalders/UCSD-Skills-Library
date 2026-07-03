# Scheduler Adapters

Use this reference when installing, checking, or removing fallback OS-level background memory jobs.

Prefer TritonAI Harness scheduled automations when available. OS-level schedulers are a fallback for local jobs that do not need to appear in the TritonAI Harness thread history.

## Contents

- Common inputs
- macOS LaunchAgent
- Windows Task Scheduler
- Linux fallback
- Verification

## Common Inputs

- Memory root: `~/.agents/ucsd/data/memory` on macOS/Linux or `%USERPROFILE%\.agents\ucsd\data\memory` on Windows.
- Daily prompt: `<memory-root>/.memory/prompts/daily-sync.md`
- Weekly prompt: `<memory-root>/.memory/prompts/weekly-cleanup.md`
- Logs: `<memory-root>/.memory/logs/`
- Daily job name: `TritonAI Memory Daily`
- Weekly job name: `TritonAI Memory Weekly`
- Agent command: resolve the absolute managed agent command before writing scheduler entries.

For fallback OS-level jobs, call the chosen local agent command directly with an absolute path. Replace `AGENT_COMMAND` with the resolved command before writing scheduler entries:

```sh
"AGENT_COMMAND" run --dir "$HOME/.agents/ucsd/data/memory" "$(cat "$HOME/.agents/ucsd/data/memory/.memory/prompts/daily-sync.md")"
```

Background schedulers often do not inherit an interactive shell `PATH`, so replace `AGENT_COMMAND` with an absolute path.

## macOS LaunchAgent

Create one plist per job under `~/Library/LaunchAgents/`.

Daily label:

```text
edu.ucsd.tritonai.memory.daily
```

Weekly label:

```text
edu.ucsd.tritonai.memory.weekly
```

Use `/bin/zsh -lc` so paths with spaces and user shell expansion can be handled in one command string. Replace `AGENT_COMMAND` with the resolved absolute command before writing.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>edu.ucsd.tritonai.memory.daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/zsh</string>
    <string>-lc</string>
    <string>cd "$HOME/.agents/ucsd/data/memory" &amp;&amp; "AGENT_COMMAND" run --dir "$HOME/.agents/ucsd/data/memory" "$(cat "$HOME/.agents/ucsd/data/memory/.memory/prompts/daily-sync.md")" >> "$HOME/.agents/ucsd/data/memory/.memory/logs/daily-sync.log" 2&gt;&amp;1</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key><integer>8</integer>
    <key>Minute</key><integer>0</integer>
  </dict>
  <key>RunAtLoad</key>
  <false/>
</dict>
</plist>
```

Install:

```sh
launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/edu.ucsd.tritonai.memory.daily.plist"
launchctl enable "gui/$(id -u)/edu.ucsd.tritonai.memory.daily"
```

Uninstall:

```sh
launchctl bootout "gui/$(id -u)/edu.ucsd.tritonai.memory.daily" 2>/dev/null || true
rm "$HOME/Library/LaunchAgents/edu.ucsd.tritonai.memory.daily.plist"
```

For weekly cleanup, use `Weekday` in `StartCalendarInterval`:

```xml
<key>StartCalendarInterval</key>
<dict>
  <key>Weekday</key><integer>1</integer>
  <key>Hour</key><integer>9</integer>
  <key>Minute</key><integer>0</integer>
</dict>
```

## Windows Task Scheduler

Use a user-level scheduled task. Prefer PowerShell because it handles quoting better than `schtasks.exe`.

Daily task:

```powershell
$memoryRoot = Join-Path $env:USERPROFILE '.agents\ucsd\data\memory'
$agent = 'AGENT_COMMAND'
$promptPath = Join-Path $memoryRoot '.memory\prompts\daily-sync.md'
$logPath = Join-Path $memoryRoot '.memory\logs\daily-sync.log'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"Set-Location '$memoryRoot'; `$prompt = Get-Content -Raw '$promptPath'; & '$agent' run --dir '$memoryRoot' `$prompt *> '$logPath'`""
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00am
Register-ScheduledTask -TaskName 'TritonAI Memory Daily' -Action $action -Trigger $trigger -Description 'Run TritonAI local memory daily sync' -Force
```

Weekly task:

```powershell
$memoryRoot = Join-Path $env:USERPROFILE '.agents\ucsd\data\memory'
$agent = 'AGENT_COMMAND'
$promptPath = Join-Path $memoryRoot '.memory\prompts\weekly-cleanup.md'
$logPath = Join-Path $memoryRoot '.memory\logs\weekly-cleanup.log'
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument "-NoProfile -ExecutionPolicy Bypass -Command `"Set-Location '$memoryRoot'; `$prompt = Get-Content -Raw '$promptPath'; & '$agent' run --dir '$memoryRoot' `$prompt *> '$logPath'`""
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 9:00am
Register-ScheduledTask -TaskName 'TritonAI Memory Weekly' -Action $action -Trigger $trigger -Description 'Run TritonAI local memory weekly cleanup' -Force
```

Check:

```powershell
Get-ScheduledTask -TaskName 'TritonAI Memory Daily','TritonAI Memory Weekly'
```

Uninstall:

```powershell
Unregister-ScheduledTask -TaskName 'TritonAI Memory Daily' -Confirm:$false
Unregister-ScheduledTask -TaskName 'TritonAI Memory Weekly' -Confirm:$false
```

## Linux Fallback

Prefer a systemd user timer when available. Use cron only when systemd user services are unavailable.

Cron examples:

```cron
0 8 * * * cd "$HOME/.agents/ucsd/data/memory" && "AGENT_COMMAND" run --dir "$HOME/.agents/ucsd/data/memory" "$(cat "$HOME/.agents/ucsd/data/memory/.memory/prompts/daily-sync.md")" >> "$HOME/.agents/ucsd/data/memory/.memory/logs/daily-sync.log" 2>&1
0 9 * * 0 cd "$HOME/.agents/ucsd/data/memory" && "AGENT_COMMAND" run --dir "$HOME/.agents/ucsd/data/memory" "$(cat "$HOME/.agents/ucsd/data/memory/.memory/prompts/weekly-cleanup.md")" >> "$HOME/.agents/ucsd/data/memory/.memory/logs/weekly-cleanup.log" 2>&1
```

## Verification

After installing schedules:

1. Confirm the scheduler entry exists.
2. Run the daily command manually once.
3. Check `.memory/logs/`.
4. Confirm at least one note or run report changed.
5. Record schedule names and next-run expectations in `.memory/config.json`.
