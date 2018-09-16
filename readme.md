## Auto FEH

# Features
- Automation based on image-recongnition
- Server API for remote control
- Support different resolutions
- Support complex logics (finite state machine), e.g. recovery from "play in another device"

# How to install

- Install python3: https://www.python.org/downloads/
- Run cmd: pip install requirements.txt

# How to use

- Ensure the title of emulator window is "(feh)" so that the script can recongize it
- Run cmd as administrator: python server.py
- Open urls in browser to control the script
    - http://localhost:3388/ , check current tasks
    - http://localhost:3388/maps/bhb/{N} (in which N should be an integer), add bound hero battle task which loops for N times
    - http://localhost:3388/maps/wrd/{N} (in which N should be an integer), add weekly rivial domain task which loops for N times
    - http://localhost:3388/events/fb/{N} (in which N should be an integer), add forging bonds task which loops for N times

# Lifecycle of task

- loop
- sleep
- wait
- find
- delay or none
- last or end or stop or reset(TODO)