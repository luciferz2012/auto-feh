## Auto FEH

# Features
- Automation based on image-recognition
- Server API for remote control
- Support different resolutions
- Support complex logics (finite state machine), e.g. recovery from "play in another device"

# How to install

- Install python3: https://www.python.org/downloads/
- Run cmd: pip install -r requirements.txt

# How to use

- Ensure the title of emulator window is "(feh)" so that the script can recongize it
- Run cmd as administrator: python server.py
- Open urls in browser to control the script
    - http://localhost:3388/ , check current tasks
    - http://localhost:3388/maps/bhb/{N} (in which N should be an integer), add bound hero battle task which loops for N times
    - http://localhost:3388/maps/wrd/{N} (in which N should be an integer), add weekly rivial domain task which loops for N times
    - http://localhost:3388/events/fb/{N} (in which N should be an integer), add forging bonds task which loops for N times
- If running the script through Teamviewer, run cmd to close the session window: python teamviewer.py

# Script

Scripts are stored in data folder. Each script is a json file with states, start, width and height properties. The start property indicates the script to start as which state. The width and height properties indicate the script what resolution the images are cliped from. Then the script will resize all images to data_XXXxXXX folder to adapt to current resolution of emulator. If new images are added, please remove the old data_XXXxXXX folder to re-resize all images.

In each state, the script searches for images shown in the emulator and clickes the best match. For example, in the following state "clear2", the script searches for "title-stage-clear.png" and "title-game-over.png". If it finds the former, it clickes it and switches to state "confirm". If it finds the later, it clickes it and switches to state "give-up". The " __ sleep __ " indicates that the script should sleep for 60 seconds before searching. If no images are found, it switches to state "cancel" as " __ none __ " indicates.

```json
"clear2": {
    "__sleep__": 60,
    "__none__": "cancel",
    "title-stage-clear.png": "confirm",
    "title-game-over.png": "give-up"
},
```

Predefined properties of state:
- __ loop __ , loop for current states (until N times or none) and switch to the first next state
- __ sleep __ , sleep before searching
- __ wait __ , wait for each images during searching
- __ delay __ , delay before click (after searching)
- __ none __ , if no images are found, switch to this state

Predefined state (no click):
- __ end __: normal end of a task
- __ stop __: error end of a task (recovery is possible)
- __ reset __: error end of a task (recovery is impossible, the emulator should be reset, not implemented yet)

# 特性

- 基于图片识别的自动化脚本
- 提供远程控制API
- 支持不同的模拟器分辩率
- 支持复杂逻辑（有限状态机），如手机端登录后，模拟器端退出，等手机端玩累了或配置好再远程控制模拟器重新执行任务

# 安装

- 安装Python3： https://www.python.org/downloads
- 命令行运行： pip install -r requirements.txt

# 使用

- 确保模拟器窗口的名称为 "(feh)" ，以便脚本识别
- 以管理员身份在命令行运行： python server.py
- 在浏览器中打开url网址来控制脚本
    - http://localhost:3388/ , 查看当前任务状态
    - http://localhost:3388/maps/bhb/{N} (N是整数), 添加N次绊英雄战任务
    - http://localhost:3388/maps/wrd/{N} (N是整数), 添加N次压制战任务
    - http://localhost:3388/events/fb/{N} (N是整数), 添加N次搜集思念任务
- 如果通过Teamviewer来控制脚本，可运行以下命令来关闭弹窗： python teamviewer.py

# 脚本

脚本保存在data文件夹，每个脚本是个包含states（状态）, start, width, height属性的json文件，其中，start属性表明脚本开始时的状态，width和height属性表明脚本对应图片是在什么分辨率下截取的。当脚本启动时，它会自动按当前模拟器的分辨率对图片进行调整，并保存到data_XXXxXXX文件夹中。当添加了新图片时，请删除data_XXXxXXX文件夹以便重新调整所有图片。

在每个状态（state）下，脚本会在模拟器当前显示的画面中搜索若干图片并点击最符合的结果。例如，在以下clear2状态中，脚本搜索了title-stage-clear.png及title-game-over.png，如找到了前者，则点击通关图片，并跳转到confirm状态，如找到后者，则点击后跳转到give-up状态。 __ sleep __ 属性表明脚本在当前状态下先停顿60秒，再进行搜索。如果两个图片都没找到，则按 __ none __ 属性跳转到cancel状态。

```json
"clear2": {
    "__sleep__": 60,
    "__none__": "cancel",
    "title-stage-clear.png": "confirm",
    "title-game-over.png": "give-up"
},
```

预定义的状态属性:
- __ loop __ , 重复本状态的次数，重复完或找不到时，跳转到第一个符合要求的状态
- __ sleep __ , 搜索前停顿秒数
- __ wait __ , 每个图片搜索时的等待秒数
- __ delay __ , 搜索到图片后，点击前停顿的秒数
- __ none __ , 当找不到任何指定的图片时，跳转到该状态

预定义的状态:
- __ end __: 任务正常结束
- __ stop __: 任务异常结束（可恢复）
- __ reset __: 任务异常结束（不可恢复，需要重启模拟器，尚未实现）
