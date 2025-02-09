import json
import matplotlib.pyplot as plt
import numpy as np
import cv2
from config import *
import numpy as np
from pathlib import Path

# plot map util
def plot_map(file_path,fig_path,show=0):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Plotting the data
    fig, ax = plt.subplots(figsize=(12, 8))

    # Convert data to numpy array for easier manipulation
    data_array = np.array(data)
    data_array = data_array.T
    rows, cols = data_array.shape

    # Assigning a color to each unique value in the matrix (non-zero)
    unique_values = np.unique(data_array[data_array != 0])
    color_map = {val: plt.cm.rainbow(i / len(unique_values)) for i, val in enumerate(unique_values)}

    for i in range(rows):
        for j in range(cols):
            if data_array[i, j] != 0:  # Skip zeros
                ax.scatter(j, -i, color=color_map[data_array[i, j]], s=100)

    # Enhance the plot for visualization
    ax.set_title('Scatter Plot of Matrix Values', fontsize=16)
    ax.set_xlabel('Column Index', fontsize=14)
    ax.set_ylabel('Row Index', fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xlim(-1, cols)
    ax.set_ylim(-rows, 1)
    if show:
        plt.show()
    else:
        plt.savefig(fig_path)
    
        
# template matching util
# 用 map[x][y] 来访问对应坐标的方块

def get_image_hash(image):
    # 取样本像素点的rgb，计算hash值
    value = ''
    for x in range(2, 8):
        for y in range(2, 8):
            r, g, b = image.getpixel((x*3, y*3))
            value += "({}, {}, {})".format(r, g, b)
    return hash(value)
def get_map_1(image):
    game_map = []
    _, _, area_width, area_height = image.getbbox()
    SQUARE_WIDTH = area_width / COL_NUM
    SQUARE_HEIGHT = area_height / ROW_NUM
    for x in range(COL_NUM):
        a_col = []
        for y in range(ROW_NUM):
            square = image.crop((
                x * SQUARE_WIDTH, y * SQUARE_HEIGHT,
                (x+1) * SQUARE_WIDTH, (y+1) * SQUARE_HEIGHT))
            a_col.append(get_image_hash(square))
            square.save("log/figs/({x},{y}).png".format(x=x,y=y))
        game_map.append(a_col)
    return game_map

# check if a image is blank
# we compare the middle 1/3 of the image, if it fills with the same color, then blank
def check_blank(im):
    cropped_image = im.crop((13, 13, 26, 26))
    im_array = np.array(cropped_image).reshape(-1,3)
    return np.array_equal(np.max(im_array, axis=0) - np.min(im_array, axis=0),  np.array([0,0,0]))

def get_same_imgs_3(square,image,SQUARE_WIDTH,SQUARE_HEIGHT,game_map):# Convert PIL images to OpenCV format (NumPy arrays)
    res = []
    res_dbg = []
    dbg_mat = []
    for x in range(COL_NUM):
        for y in range(ROW_NUM):
            if not log_enabled and game_map[x][y] != -1:
                break
            square_xy = image.crop((
                x * SQUARE_WIDTH, y * SQUARE_HEIGHT,
                (x+1) * SQUARE_WIDTH, (y+1) * SQUARE_HEIGHT))           
            # first cast into same shape
            min_shape =  [min(x, y) for x, y in zip(np.array(square_xy).shape, np.array(square).shape)]
            # print(min_shape)
            cs = 5 # crop size
            crop_square_xy = np.array(square_xy).astype(np.int64)[cs:min_shape[0]-cs,cs:min_shape[1]-cs,:]
            crop_square = np.array(square).astype(np.int64)[cs:min_shape[0]-cs,cs:min_shape[1]-cs,:]
            diff = crop_square_xy-crop_square
            dist = np.linalg.norm(diff.flatten(),ord=1)
            if dist < 100000.:
                res.append((x,y))
                #print(dist,"(small)")
            else:
                #print(dist)
                pass
    return res

def get_map_3(image):
    max_ind = 1
    _, _, area_width, area_height = image.getbbox()
    SQUARE_WIDTH = area_width / COL_NUM
    SQUARE_HEIGHT = area_height / ROW_NUM
    game_map = [ [-1 for j in  range(ROW_NUM)] for i in range(COL_NUM)]
    for x in range(COL_NUM):
        for y in range(ROW_NUM):
            square = image.crop((
                x * SQUARE_WIDTH, y * SQUARE_HEIGHT,
                (x+1) * SQUARE_WIDTH, (y+1) * SQUARE_HEIGHT))
            if log_enabled:
                save_path = Path("log/figs/({x},{y}).png".format(x=x,y=y))
                save_path.parent.mkdir(parents=True, exist_ok=True)
                square.save(save_path)
            if check_blank(square) == True:
                if check_template_match:
                    assert game_map[x][y] == -1
                game_map[x][y] = 0
            elif game_map[x][y] == -1:
                same_imgs = get_same_imgs_3(square,image,SQUARE_WIDTH,SQUARE_HEIGHT,game_map)
                # print("(x,y)=({x},{y})".format(x=x,y=y),same_imgs)
                for ix,iy in same_imgs:
                    #print("(ix,iy)=({ix},{iy})".format(ix=ix,iy=iy))
                    if check_template_match:
                        assert game_map[ix][iy] == -1
                    game_map[ix][iy] = max_ind
                max_ind += 1
                
    return game_map


def get_same_imgs_2(square,image,SQUARE_WIDTH,SQUARE_HEIGHT):# Convert PIL images to OpenCV format (NumPy arrays)
    # match template with cv2
    # this step compares grey value
    search_image = np.array(image)
    template = np.array(square)
    
    # Convert to grayscale (if needed)
    if search_image.shape[-1] == 4:  # If RGBA, remove alpha channel
        search_image = search_image[:, :, :3]
    if template.shape[-1] == 4:
        template = template[:, :, :3]
        
    # Crop edges of the template (adjust the crop dimensions as needed)
    crop_top = crop_bottom = crop_left = crop_right = 5
    cropped_template = template[crop_top:template.shape[0]-crop_bottom, 
                                 crop_left:template.shape[1]-crop_right]
    mode = 'color'
    assert mode in ['color','grey']
    if mode == 'color':
        # Match template on each color channel separately
        result_r = cv2.matchTemplate(search_image[:, :, 0], cropped_template[:, :, 0], cv2.TM_CCOEFF_NORMED)
        result_g = cv2.matchTemplate(search_image[:, :, 1], cropped_template[:, :, 1], cv2.TM_CCOEFF_NORMED)
        result_b = cv2.matchTemplate(search_image[:, :, 2], cropped_template[:, :, 2], cv2.TM_CCOEFF_NORMED)

        # Combine the results by averaging them
        result = np.maximum(result_r,result_g,result_b)
    elif mode == 'grey':
        gray_search_image = cv2.cvtColor(search_image, cv2.COLOR_BGR2GRAY)
        gray_cropped_template = cv2.cvtColor(cropped_template, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(gray_search_image, gray_cropped_template, cv2.TM_CCOEFF_NORMED)

    # Threshold for a match
    threshold = 0.8  # Matches above 80% confidence

    # Find all locations where the match is above the threshold
    locations = np.where(result >= threshold)

    # Extract the dimensions of the template
    template_height, template_width = cropped_template.shape[:2]

    # Calculate the center coordinates of each match
    pixel_coordinates = [
        (int(x + template_width / 2), int(y + template_height / 2))
        for x, y in zip(locations[1], locations[0])
    ]
    
    coords = set()
    
    for x,y in pixel_coordinates:
        coords.add((int(x/SQUARE_WIDTH),int(y/SQUARE_HEIGHT)))
    
    coords = list(coords)
    # remove some different color figures
    res = []
    for x,y in coords:
        square_xy = image.crop((
            x * SQUARE_WIDTH, y * SQUARE_HEIGHT,
            (x+1) * SQUARE_WIDTH, (y+1) * SQUARE_HEIGHT))           
        # first cast into same shape
        min_shape =  [min(x, y) for x, y in zip(np.array(square_xy).shape, np.array(square).shape)]
        # print(min_shape)
        cs = 5 # crop size
        crop_square_xy = np.array(square_xy).astype(np.int64)[cs:min_shape[0]-cs,cs:min_shape[1]-cs,:]
        crop_square = np.array(square).astype(np.int64)[cs:min_shape[0]-cs,cs:min_shape[1]-cs,:]
        diff = crop_square_xy-crop_square
        dist = np.linalg.norm(diff.flatten(),ord=1)
        threshold = 100000.
        if dist < threshold:
            res.append((x,y))
    return res
def get_map_2(image):
    max_ind = 1
    _, _, area_width, area_height = image.getbbox()
    SQUARE_WIDTH = area_width / COL_NUM
    SQUARE_HEIGHT = area_height / ROW_NUM
    game_map = [ [-1 for j in  range(ROW_NUM)] for i in range(COL_NUM)]
    for x in range(COL_NUM):
        for y in range(ROW_NUM):
            square = image.crop((
                x * SQUARE_WIDTH, y * SQUARE_HEIGHT,
                (x+1) * SQUARE_WIDTH, (y+1) * SQUARE_HEIGHT))
            if log_enabled:
                save_path = Path("log/figs/({x},{y}).png".format(x=x,y=y))
                save_path.parent.mkdir(parents=True, exist_ok=True)
                square.save(save_path)
            if check_blank(square) == True:
                assert game_map[x][y] == -1
                game_map[x][y] = 0
            elif game_map[x][y] == -1:
                same_imgs = get_same_imgs_2(square,image,SQUARE_WIDTH,SQUARE_HEIGHT)
                if check_template_match:
                    print("(x,y)=({x},{y})".format(x=x,y=y),same_imgs)
                for ix,iy in same_imgs:
                    if check_template_match:
                        print("(ix,iy)=({ix},{iy})".format(ix=ix,iy=iy))
                        assert game_map[ix][iy] == -1
                    game_map[ix][iy] = max_ind
                max_ind += 1
                
    return game_map