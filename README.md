# hangup.py
Detects hangups and slowdowns by running a short sleep in a loop and timing the duration.
Asynchronously logs event to syslog, local log file, and sends a GUI notification to user.


#### Usage
`python3 hangup.py` or `./hangup.py`
