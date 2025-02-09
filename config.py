# -*- coding: utf-8 -*-

log_enabled = True  # 是否输出日志
INIT_REORDER_COUNTER = 2  # 限制使用重列的次数，防止重列次数用完后，陷入无限循环。一局游戏中，必须使用2次重列的概率非常非常低
check_template_match = True

WINDOW_TITLE = 'QQ游戏 - 连连看角色版'
COL_NUM = 19
ROW_NUM = 11
EMPTY = 0
GAME_AREA_LEFT_RATIO = 14 / 800.0
GAME_AREA_TOP_RATIO = 181 / 600.0
GAME_AREA_RIGHT_RATIO = 603 / 800.0
GAME_AREA_BOTTOM_RATIO = 566 / 600.0
REORDER_BUTTON_X_RATIO = 651 / 800.0
REORDER_BUTTON_Y_RATIO = 201 / 600.0

sleep_ave = 0.1 # sleep time between clicks, could also use "adaptive"
