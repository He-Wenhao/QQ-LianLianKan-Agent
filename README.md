# 演示（Demo）
演示视频可在 `demo` 文件夹中找到。
![lianliankan-demo-ezgif com-video-to-gif-converter (3)](https://github.com/user-attachments/assets/04eda813-a96b-4dd7-b2e6-cfd7201ca570)

# 如何运行（在 Windows 上）
1. 以管理员身份打开 `cmd`。
2. 打开 QQ 游戏 - 连连看角色版。
3. 运行代码：`python main.py`。

# 常见问题（Frequent Questions）
1. **如何设置 Python 环境？**  
   运行以下命令安装依赖：  
   ```bash
   pip install pyautogui pywin32 keyboard matplotlib numpy opencv-python json5
   ```

2. **如何设置 `config.py`？**  
   - 调试模式（Debug）：`log_enabled = True`，`check_template_match = True`，`sleep_ave = 0.1`。  
   - 正常运行模式（Runtime）：`log_enabled = False`，`check_template_match = False`，`sleep_ave = 0.5`。  
   - 如果想展示效果，可设置 `sleep_ave = 0.`。

3. **为什么必须使用管理员模式（或 sudo）？**  
   因为 QQ 连连看是以管理员权限运行的，所以我们的脚本也必须以管理员权限运行，才能与 QQ 连连看进行交互，否则 `pyautogui` 将无法工作。

4. **调试模式与工具**  
   - 当 `log_enabled = True` 且 `check_template_match = True` 时，可以通过 `log/` 文件夹中的文件和 `cmd` 输出进行调试。

5. **运行错误处理**  
   - 我们没有处理一些特殊情况，例如“无解，请点击刷新按钮重新开始”或“炸弹道具”。
   - 如果脚本崩溃，可以重新启动 Python 进程。

# 策略（Strategies）
1. **计算机视觉算法（Computer Vision Algorithm）**  
   最重要的部分是卡片分类算法。我们实现了三种算法：
   1. 使用卡片内部三个点的 RGB 值，将 `[rgb1, rgb2, rgb3]` 作为标识符进行分类。
   2. 使用 `cv2.match_template`（`cv2.TM_CCOEFF_NORMED`，置信度 0.8）在灰度图中查找相似卡片，并通过计算 RGB 矩阵的 1 范数（阈值 100000）排除不同颜色的卡片。
   3. 直接计算 RGB 矩阵差异，如果足够小，则归类为相同卡片（1 范数，阈值 100000）。
   
   其中，算法 (ii) 是最稳定的，我们在主脚本中使用它。

2. **路径搜索算法（Path Finding Algorithm）**  
   采用适当的路径搜索策略，以最快速度消除匹配的卡片。

3. **鼠标与窗口控制（Mouse and Windows Control）**  
   - 我们使用 `win32api.mouse_event` 代替 `pyautogui.click`，以减少延迟，提高点击速度。

# 致谢（Acknowledgement）
我们的代码基于开源项目：[play-lianliankan](https://github.com/plough/play-lianliankan)。





# demo
 demo video can be found in demo folder

# How to run it (on windows)
 step 1: open a cmd as administrator
 step 2: open QQ游戏 - 连连看角色版
 step 3: run the code by ``python main.py``

# Frequent Questions
 1. how to set up python environment?
 `pip install pyautogui pywin32 keyboard matplotlib numpy opencv-python json5`
 2. how to set config.py
 For debug, choose `log_enabled = True` , `check_template_match = True` and `sleep_ave = 0.1`; for running time, use both of them False an set `sleep_ave = 0.5`; can also set `sleep_ave = 0.` to show off
 3. why must use administrator mode(or sudo)? 
 Because QQ lianliankan is run as administrator, so we must run our script also as administrator to interact with QQ lianliankan. Otherwise pyautogui will not work.
 4. debugging mode and tools
 when we choose `log_enabled = True` , `check_template_match = True`, files in `log/` and output in cmd can be used to debug
 5. error when 
 We don't consider very special cases like “无解，请点击刷新按钮重新开始” or "炸弹道具". If the script crashes, you can re start the python process.

# Strategies
 1. computer vision algorithm
   The most important part is the card classification algorithm. We implement 3 algorithms here:
   (i) use three interier points rgb value inside the card, use the [rgb1,rgb2,rgb3] array as the identification
   (ii) use cv2.match_template cv2.TM_CCOEFF_NORMED (confidence 0.8) to find similar cards in grey value, and exclude different color ones by calculating rgb matrix difference (1 norm and threshold 100000)
   (iii) calculating rgb matrix difference, if small enough, classified to same card (1 norm and threshold 100000)
   algorithm (ii) is the most stable one. We apply it in the main scripy.
 2. path finding algorithm
 3. mouse and windows control
    we use win32api.mouse_event instead of pyautogui.click for its very low delay.



# acknowledgement
our code is based on https://github.com/plough/play-lianliankan
