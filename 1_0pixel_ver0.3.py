import os
import json
import cv2
import numpy as np
import glob
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from matplotlib.backend_bases import MouseEvent

# 1. 사용자 지정 폴더 경로
image_folder = "./datasets/2/image/"
json_folder = "./datasets/2/json/"
output_folder = "./datasets/2/mask/"

os.makedirs(output_folder, exist_ok=True)

def natural_sort_key(filename):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', os.path.basename(filename))]

IMAGE_EXTENSIONS = ['.jpg', '.png', '.jpeg']
image_files = sorted(
    [f for f in glob.glob(os.path.join(image_folder, "*")) if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS],
    key=natural_sort_key
)

json_files = {os.path.splitext(os.path.basename(f))[0]: f for f in glob.glob(os.path.join(json_folder, "*.json"))}

polygon_points = []
polygon_masks = []
current_index = 0
image = None
annotations = {}
mask_image = None
zoom_factor = 1.0
xlim, ylim = None, None

def load_json(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data

def draw_annotations(ax, annotations):
    for shape in annotations.get("shapes", []):
        points = np.array(shape["points"])
        if shape["shape_type"] == "rectangle":
            x_min, y_min = points[0]
            x_max, y_max = points[1]
            rect = Rectangle((x_min, y_min), x_max - x_min, y_max - y_min, edgecolor='red', facecolor='none', lw=1)
            ax.add_patch(rect)
        elif shape["shape_type"] == "polygon":
            poly = Polygon(points, edgecolor='red', facecolor='none', lw=1)
            ax.add_patch(poly)

def is_zoom_or_pan_active():
    toolbar = plt.get_current_fig_manager().toolbar
    return toolbar.mode in ['zoom rect', 'pan/zoom']

def on_mouse_click(event: MouseEvent):
    global polygon_points
    if is_zoom_or_pan_active():
        return

    if event.xdata is not None and event.ydata is not None:
        polygon_points.append((int(event.xdata), int(event.ydata)))
        ax.scatter(*zip(*polygon_points), c='yellow', marker='o')
        fig.canvas.draw()

def erase_polygon():
    global polygon_points, mask_image
    if len(polygon_points) > 2:
        cv2.fillPoly(mask_image, [np.array(polygon_points, dtype=np.int32)], 255)
        polygon_masks.append(np.array(polygon_points, dtype=np.int32))
        polygon_points.clear()
        refresh_display()

def refresh_display():
    global xlim, ylim
    ax.clear()
    ax.imshow(image)
    draw_annotations(ax, annotations)
    for mask in polygon_masks:
        poly_patch = Polygon(mask, edgecolor='yellow', facecolor='none', lw=2)
        ax.add_patch(poly_patch)

    if xlim and ylim:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    image_name = os.path.basename(image_files[current_index])
    ax.set_title(image_name)
    fig.canvas.draw()

def save_mask():
    global mask_image, image_files, current_index
    if mask_image is not None:
        image_name = os.path.basename(image_files[current_index])
        mask_name = os.path.splitext(image_name)[0] + "_mask.png"
        save_path = os.path.join(output_folder, mask_name)
        cv2.imwrite(save_path, mask_image)
        print(f"✔️ {save_path} 저장 완료!")

def on_key(event):
    global current_index, image, annotations, polygon_points, mask_image, xlim, ylim
    if event.key == 'z':
        erase_polygon()
    elif event.key == 'x':
        save_mask()
        current_index += 1
        if current_index >= len(image_files):
            current_index = 0
        load_image_and_json()
    elif event.key == 'd':
        current_index += 1
        if current_index >= len(image_files):
            current_index = 0
        load_image_and_json()
    elif event.key == 'a':
        current_index -= 1
        if current_index < 0:
            current_index = len(image_files) - 1
        load_image_and_json()
    elif event.key == 'u':
        if polygon_masks:
            polygon_masks.pop()
            mask_image = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
            for mask in polygon_masks:
                cv2.fillPoly(mask_image, [mask], 255)
            refresh_display()
        else:
            print("제거할 폴리곤이 없습니다.")
    elif event.key in ['up', 'down', 'left', 'right']:
        move_view(event.key)

def move_view(direction):
    global xlim, ylim
    move_step = 50  # 이동 거리 증가
    if xlim and ylim:
        if direction == 'up':
            ylim = (ylim[0] - move_step, ylim[1] - move_step)
        elif direction == 'down':
            ylim = (ylim[0] + move_step, ylim[1] + move_step)
        elif direction == 'left':
            xlim = (xlim[0] - move_step, xlim[1] - move_step)
        elif direction == 'right':
            xlim = (xlim[0] + move_step, xlim[1] + move_step)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        fig.canvas.draw()

def on_scroll(event):
    global xlim, ylim, zoom_factor
    base_scale = 1.2

    if event.step > 0:  # 스크롤 업(확대)
        scale_factor = base_scale
    elif event.step < 0:  # 스크롤 다운(축소)
        scale_factor = 1.0 / base_scale
    else:
        return

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    x_range = (xlim[1] - xlim[0]) / 2
    y_range = (ylim[1] - ylim[0]) / 2
    x_center = (xlim[0] + xlim[1]) / 2
    y_center = (ylim[0] + ylim[1]) / 2

    new_x_range = x_range * scale_factor
    new_y_range = y_range * scale_factor

    ax.set_xlim([x_center - new_x_range, x_center + new_x_range])
    ax.set_ylim([y_center - new_y_range, y_center + new_y_range])

    fig.canvas.draw()


def load_image_and_json():
    global image, annotations, polygon_points, mask_image, polygon_masks, xlim, ylim
    image_path = image_files[current_index]
    json_path = json_files.get(os.path.splitext(os.path.basename(image_path))[0])

    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mask_image = np.zeros((image.shape[0], image.shape[1]), dtype=np.uint8)
    polygon_masks.clear()
    polygon_points.clear()

    if json_path:
        annotations = load_json(json_path)
    else:
        annotations = {"shapes": []}

    if xlim and ylim:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    refresh_display()

fig, ax = plt.subplots()
fig.canvas.mpl_connect("button_press_event", on_mouse_click)
fig.canvas.mpl_connect("key_press_event", on_key)
fig.canvas.mpl_connect("scroll_event", on_scroll)

load_image_and_json()
plt.show()
