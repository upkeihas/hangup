#!/usr/bin/env python3
#
# Detect possible system hangs
#
# Sleep defined amount of millis in a loop and measure how long the sleep took in real-time to detect slowdowns.
# Asynchronously logs event to syslog, local log file and sends a GUI notification for the user.
#

from datetime import datetime
from subprocess import run
from time import perf_counter, sleep

import asyncio


NOTIFY_PATH = '/usr/bin/notify-send'
LOGGER_PATH = '/usr/bin/logger'
OUTFILE = 'hangup.txt'
SLEEP_MILLIS = 100  # 10..1000
SLEEP_SECONDS = SLEEP_MILLIS/1000
SLOWDOWN_THRESHOLD = 1.03  # times SLEEP_SECONDS
FREEZE_THRESHOLD = 2  # times SLEEP_SECONDS

_HANGUPS = []


async def _log_to_file(msg: str) -> None:
  """
  Write hangup event to log file.
  """
  with open(OUTFILE, 'a') as _out:
    _out.write(msg + '\n')

async def _log_to_syslog(msg: str) -> None:
  """
  Generate a system log entry about detected event.
  """
  run([LOGGER_PATH,
       f'--priority={"error" if "ERROR" in msg else "warning"}',
       msg])

async def _notify(msg: str) -> None:
  """
  Generate a system notification about detected event.
  """
  run([NOTIFY_PATH,
       '--app-name=hangup.py',
       # '--urgency=critical',
       '--icon=dialog-warning',
       msg])

def _hangup(start: float, end: float) -> None:
  """
  Hangup event handler.
  Spam the console, write to syslog and log file and launch a system notification!
  """
  _duration = end - start
  _msg = f'{datetime.now()} | {"ERROR: Possible system freeze!" if _duration >= (SLEEP_SECONDS*FREEZE_THRESHOLD) else "WARNING: Possible system slowdown!"
                              } Expected / Actual duration: < {SLEEP_SECONDS*SLOWDOWN_THRESHOLD} / {_duration} s'
  print(_msg)
  _HANGUPS.append(_msg)
  asyncio.run(_log_to_syslog(_msg))
  asyncio.run(_log_to_file(_msg))
  asyncio.run(_notify(_msg))


try:
  print('Begin sense(less) loop!')
  print('Use CTRL-C to quit!')
  i = 0
  while True:
    i += 1
    print(f'{i}\r', end='')
    _start = perf_counter()
    sleep(SLEEP_SECONDS)
    _end = perf_counter()
    _duration = _end - _start

    if _duration >= (SLEEP_SECONDS*SLOWDOWN_THRESHOLD):
      _hangup(_start, _end)


except KeyboardInterrupt:
  if _HANGUPS:
    print('')
    for _hu in _HANGUPS:
      print(_hu)
  print('Terminated.')
