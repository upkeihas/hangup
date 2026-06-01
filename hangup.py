#!/bin/env python3
#
# Detect possible system hangs
#
# sleep short amount of millis and measure how long the break really was.
# Alerts in every channel if freeze detected.
#

from datetime import datetime
from subprocess import run
from time import perf_counter, sleep

import asyncio


NOTIFY_PATH = '/usr/bin/notify-send'
OUTFILE = 'hangup.txt'
SLEEP_MILLIS = 100
SLEEP_SECONDS = SLEEP_MILLIS/1000
SLOWDOWN_THRESHOLD = 1.05  # times SLEEP_SECONDS
FREEZE_THRESHOLD = 2

_HANGUPS = []


async def _log(msg: str) -> None:
  """
  Write hangup event to log file.
  """
  with open(OUTFILE, 'a') as _out:
    _out.write(msg + '\n')


async def _notify(msg: str) -> None:
  """
  Generate a system notification about detected freeze.
  """
  run([NOTIFY_PATH,
       '--app-name=Hangup.py',
       # '--urgency=critical',
       '--icon=dialog-warning',
       msg])


def _hangup(start: float, end: float, freeze: bool) -> None:
  """
  Hangup handler. Spam the console, write log file and launch a system notification!
  """
  _duration = end - start
  _msg = f'{datetime.now()} | {"ERROR: Possible system freeze!" if freeze else "WARNING: Possible system slowdown!"
                              } Expected / Actual duration: <{SLEEP_SECONDS*SLOWDOWN_THRESHOLD} / {_duration} s'
  print(_msg)
  _HANGUPS.append(_msg)
  asyncio.run(_log(_msg))
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

    if _duration >= (SLEEP_SECONDS*FREEZE_THRESHOLD):
      _hangup(_start, _end, True)
    elif _duration >= (SLEEP_SECONDS*SLOWDOWN_THRESHOLD):
      _hangup(_start, _end, False)


except KeyboardInterrupt:
  if _HANGUPS:
    print('')
    for _hu in _HANGUPS:
      print(_hu)
  print('Terminated.')
