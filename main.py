#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyautogui
import time
import win32con
import win32gui
import win32api
import random
from config import *
import keyboard
from utils import plot_map
import json
from utils import get_map_1,get_map_2,get_map_3

get_map = get_map_2

square_remove_counter = 0  # 追踪被移除的小方块的数量


def get_sleep_time(sleep_ave):
    if sleep_ave == 'adaptive':
        if random.randint(1, 5) == 1:
            return 1
        use_time = 0
        if square_remove_counter < 20:
            use_time = random.randint(3, 8) / 10.0
        elif square_remove_counter < 50:
            use_time = random.randint(6, 25) / 10.0
        elif square_remove_counter < 100:
            use_time = random.randint(3, 12) / 10.0
        else:
            use_time = random.randint(2, 4) / 10.0
        return use_time
    else:
        return sleep_ave


def main():
    reorder_counter = INIT_REORDER_COUNTER
    game_area_image = get_game_area_image()
    # 切割小方块，并将小方块映射为一串hash码，存到二维数组中
    game_map = get_map(game_area_image)
    # 遍历二维数组，将相同hash码的索引归为一组
    group_map = get_group_map(game_map)
    # 找到所有空白的小方块，并设置为空白值
    deal_with_empty_square(group_map, game_map)
    if log_enabled:
        json_path = 'log/map.json'
        fig_path = 'log/map.png'
        with open(json_path,'w') as file:
            json.dump(game_map,file)
        plot_map(json_path,fig_path)
    # time.sleep(100) # dbg

    while is_not_clear(game_map):
        log_print('loop begin')
        # 遍历所有hash组中的两两组合，找一个满足消除条件的
        remove_i = None
        remove_j = None
        for group in group_map.values():
            i, j = find_one_solution(group, game_map)
            if i >= 0 and j >= 0:
                remove_i = i
                remove_j = j
                break
        if log_enabled:
            print('remove i, j',remove_i,remove_j)
        # if esc, exit
        if keyboard.is_pressed('esc'):
           print('keyboard interuption')
           break
        # 如果处于异常状态，则退出程序，不要乱点鼠标了
        if is_in_invalid_state():
            log_print('异常状态，提前退出')
            break

        if remove_j is not None:
            # 如果满足消除条件，就控制鼠标，完成消除操作
            do_remove(remove_i, remove_j, group, game_map)
            global square_remove_counter
            square_remove_counter += 1

            sleep_time = get_sleep_time(sleep_ave)
            if sleep_time > 0:
                time.sleep(sleep_time)
        else:
            # 如果没有可消除的，则点击重列按钮，并重新运行所有步骤
            log_print('NO SOLUTION! Use Reorder...')
            print('game map\n',game_map)    #dbg
            #time.sleep(100)
            if reorder_counter > 0:
                reorder_counter -= 1
                click_reorder_button()
                time.sleep(5)
                main()
            log_print('NO SOLUTION!')
            break


def is_in_invalid_state():
    # 窗口关闭，或者窗口被拖动了，视为异常状态
    window_id = win32gui.FindWindow(None, WINDOW_TITLE)
    if window_id > 0:
        test_w_x1, test_w_y1, _, _ = win32gui.GetWindowRect(window_id)
        if w_x1 == test_w_x1 and w_y1 == test_w_y1:
            # 确保窗口始终处于最顶层
            win32gui.SetForegroundWindow(window_id)
            return False
    return True


def click_reorder_button():
    pyautogui.click(REORDER_BUTTON_POS)


def deal_with_empty_square(group_map, game_map):
    # 我们认为，出现次数最多的方块，就是空白方块
    empty_group = []
    empty_key = ''
    for key, group in group_map.items():
        if len(group) > len(empty_group):
            empty_group = group
            empty_key = key
    group_map.pop(empty_key)

    for p_x, p_y in empty_group:
        game_map[p_x][p_y] = EMPTY


def do_remove(i, j, group, game_map):
    point_a = group[i]
    point_b = group[j]
    click_point(point_a)
    click_point(point_b)
    remove_from_game_map(game_map, point_a, point_b)
    group.remove(point_a)
    group.remove(point_b)
    log_print("remove points: {}, {}".format(point_a, point_b))


def click_point(point):
    # 得到某个点在屏幕上的坐标
    p_x, p_y = point
    p_x *= SQUARE_WIDTH
    p_y *= SQUARE_HEIGHT
    # 再加上窗口坐标和偏移量
    p_x += GAME_AREA_X + 10
    p_y += GAME_AREA_Y + 10
    # 鼠标点击坐标
    p_x, p_y = int(p_x), int(p_y)  # Convert to integers
    win32api.SetCursorPos((p_x, p_y))  # Move the cursor to (px, py)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, p_x, p_y, 0, 0)  # Press left button
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, p_x, p_y, 0, 0)  # Release left button


def remove_from_game_map(game_map, *points):
    for point in points:
        p_x, p_y = point
        game_map[p_x][p_y] = EMPTY


def find_one_solution(group, game_map):
    for i in range(len(group)-1):
        for j in range(i + 1, len(group)):
            point_a = group[i]
            point_b = group[j]
            if is_connected(point_a, point_b, game_map):
                return i, j
    return -1, -1


def is_connected(point_a, point_b, game_map):
    a_x, a_y = point_a
    b_x, b_y = point_b
    # 1. 直接相连
    if is_connected_straight_line(a_x, a_y, b_x, b_y, game_map):
        log_print('is_connected_straight_line')
        return True
    # 2. 通过一个拐点相连
    if is_connected_by_one_help_point(a_x, a_y, b_x, b_y, game_map):
        log_print('is_connected_by_one_help_point')
        return True
    # 3. 通过两个拐点相连
    possible_help_points = get_all_possible_help_points(a_x, a_y, game_map)
    for point in possible_help_points:
        p_x, p_y = point
        if is_connected_by_one_help_point(p_x, p_y, b_x, b_y, game_map):
            log_print('is_connected_by_two_help_point, one is {}'.format(point))
            return True
    return False


def get_all_possible_help_points(a_x, a_y, game_map):
    possible_help_points = []
    # x 轴
    for x in range(0, a_x)[::-1]:
        if not add_possible_help_point(possible_help_points, x, a_y, game_map):
            break
    for x in range(a_x + 1, len(game_map)):
        if not add_possible_help_point(possible_help_points, x, a_y, game_map):
            break
    # y 轴
    for y in range(0, a_y)[::-1]:
        if not add_possible_help_point(possible_help_points, a_x, y, game_map):
            break
    for y in range(a_y + 1, len(game_map[0])):
        if not add_possible_help_point(possible_help_points, a_x, y, game_map):
            break
    return possible_help_points


def is_connected_by_one_help_point(a_x, a_y, b_x, b_y, game_map):
    # 以a为标定点，遍历所有可能的拐点
    possible_help_points = get_all_possible_help_points(a_x, a_y, game_map)

    for point in possible_help_points:
        p_x, p_y = point
        if is_connected_straight_line(p_x, p_y, b_x, b_y, game_map):
            return True
    return False


def add_possible_help_point(possible_help_points, point_x, point_y, game_map):
    if game_map[point_x][point_y] == EMPTY:
        possible_help_points.append((point_x, point_y))
        return True
    return False


def is_connected_straight_line(a_x, a_y, b_x, b_y, game_map):
    if a_x == b_x:
        min_y = min(a_y, b_y)
        max_y = max(a_y, b_y)
        for y in range(min_y + 1, max_y):
            if game_map[a_x][y] != EMPTY:
                return False
        return True
    if a_y == b_y:
        min_x = min(a_x, b_x)
        max_x = max(a_x, b_x)
        for x in range(min_x + 1, max_x):
            if game_map[x][a_y] != EMPTY:
                return False
        return True
    return False


def is_not_clear(game_map):
    for row in game_map:
        for square_hash in row:
            if square_hash != 0:
                return True
    return False


def get_game_area_image():
    # 获取“连连看”窗口的坐标
    window_id = win32gui.FindWindow(None, WINDOW_TITLE)
    while not window_id:
        print('window not found, sleep 5s...')
        time.sleep(5)
        window_id = win32gui.FindWindow(None,WINDOW_TITLE)
    assert(window_id > 0)
    global w_x1, w_y1
    w_x1, w_y1, w_x2, w_y2 = win32gui.GetWindowRect(window_id)
    w_width = w_x2 - w_x1
    w_height = w_y2 - w_y1
    log_print('window rect: ({}, {}, {}, {})'.format(w_x1, w_y1, w_width, w_height))

    # 全屏幕截图
    win32gui.SetForegroundWindow(window_id)
    time.sleep(0.5)
    screen = pyautogui.screenshot()
    if log_enabled:
        screen.save("log/figs/original.png") # dbg
    # 得到游戏区域的图片
    global GAME_AREA_X, GAME_AREA_Y
    GAME_AREA_X = w_x1 + GAME_AREA_LEFT_RATIO * w_width
    GAME_AREA_Y = w_y1 + GAME_AREA_TOP_RATIO * w_height
    game_area_end_x = w_x1 + GAME_AREA_RIGHT_RATIO * w_width
    game_area_end_y = w_y1 + GAME_AREA_BOTTOM_RATIO * w_height

    # 顺便拿到“重列”按钮的坐标
    global REORDER_BUTTON_POS
    REORDER_BUTTON_POS = (
        w_x1 + REORDER_BUTTON_X_RATIO * w_width, w_y1 + REORDER_BUTTON_Y_RATIO * w_height)
    log_print('reorder position',REORDER_BUTTON_POS)
    cropped_screen = screen.crop((GAME_AREA_X, GAME_AREA_Y, game_area_end_x, game_area_end_y))
    if log_enabled:
        cropped_screen.save("log/cropped_screen.png") # dbg
        
    _, _, area_width, area_height = cropped_screen.getbbox()
    global SQUARE_WIDTH, SQUARE_HEIGHT
    SQUARE_WIDTH = area_width / COL_NUM
    SQUARE_HEIGHT = area_height / ROW_NUM
    return cropped_screen




def all_elements_equal(lst):
    return all(element == lst[0] for element in lst) if lst else True





def get_group_map(game_map):
    group_map = {}
    for x in range(len(game_map)):
        for y in range(len(game_map[0])):
            value = game_map[x][y]
            if value not in group_map:
                group_map[value] = []
            group_map.get(value).append((x, y))

    return group_map

########################
# for debug
########################

def log_print(*args):
    if log_enabled:
        print(*args)
        
        
def find_reorder_with_matching():
    location = pyautogui.locateCenterOnScreen(image='figs/reorder.png',confidence=0.8)
    pyautogui.click(location)
    #time.sleep(1)
    log_print("reorder position with matching",location)
    
def repeated_lianxi():
    for _ in range(10):
        main()
        print('one loop done!')
        time.sleep(3)
        location = pyautogui.locateCenterOnScreen(image='figs/lianxi.png',confidence=0.8)
        pyautogui.click(location)


if __name__ == "__main__":
    main()
    print('done!')
