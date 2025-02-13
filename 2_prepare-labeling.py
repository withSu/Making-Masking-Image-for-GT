import os
import cv2
import numpy as np
import glob
import re
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from matplotlib.backend_bases import MouseEvent
import shutil

# ✅ 사용자 지정 폴더 경로 설정
A_folder = "./datasets/1/image/"  # JPG 이미지 폴더
B_folder = "./datasets/1/mask/"  # PNG 마스크 폴더
D_folder = "./datasets/1/0pixel"  # 0픽셀로 저장할 폴더

# ✅ 출력 폴더 생성
os.makedirs(D_folder, exist_ok=True)

# ✅ 자연 정렬 함수
def natural_sort_key(filename):
    """파일명을 숫자와 문자로 분리하여 자연스럽게 정렬"""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', os.path.basename(filename))]

# ✅ 파일 목록 정렬하여 불러오기
jpg_files = sorted(glob.glob(os.path.join(A_folder, "*.jpg")), key=natural_sort_key)
png_files = sorted(glob.glob(os.path.join(B_folder, "*.png")), key=natural_sort_key)

# ✅ 파일 매칭 (JPG 이름과 PNG에서 "_mask" 제거한 이름을 비교)
image_pairs = []
for jpg_file in jpg_files:
    base_name = os.path.splitext(os.path.basename(jpg_file))[0]  # JPG 파일명 (확장자 제외)
    
    # PNG 파일 리스트에서 '_mask'를 제거한 이름과 비교
    matching_png = next(
        (png for png in png_files if os.path.splitext(os.path.basename(png))[0] == f"{base_name}_mask"), 
        None
    )
    
    if matching_png:
        image_pairs.append((jpg_file, matching_png))

# ✅ 매칭 확인
if len(image_pairs) == 0:
    print("🚨 JPG와 PNG 매칭된 파일이 없습니다! 파일명을 확인하세요.")
else:
    print(f"✔️ 총 {len(image_pairs)}개의 이미지가 매칭되었습니다.")

# ✅ 전역 변수
current_index = 0
image = None
mask = None
overlayed_image = None  # 마스크 적용된 이미지 저장
xlim, ylim = None, None  # 확대 상태 저장
polygon_points = []
polygons = []  # 저장된 폴리곤들

def apply_black_mask(image, mask):
    """마스크 영역을 0 픽셀(검은색)으로 변환하여 적용"""
    masked_image = image.copy()
    
    # 마스크의 흰색(255) 부분을 검은색(0)으로 설정
    masked_image[mask == 255] = (0, 0, 0)
    
    return masked_image

def load_images():
    """현재 인덱스에 해당하는 JPG 이미지와 PNG 마스크를 불러와 overlay 적용"""
    global image, mask, overlayed_image, xlim, ylim, polygons, polygon_points
    
    if current_index >= len(image_pairs):
        print("✅ 모든 이미지가 완료되었습니다!")
        plt.close()
        return
    
    jpg_path, png_path = image_pairs[current_index]
    image = cv2.imread(jpg_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # OpenCV는 BGR이므로 RGB 변환

    mask = cv2.imread(png_path, cv2.IMREAD_GRAYSCALE)  # 1채널 흑백 이미지
    
    # ✅ 마스크를 적용하여 미리보기 생성 (마스크 부분만 검은색)
    mask_rgb = np.zeros_like(image)
    
    # 마스크 부분만 검은색으로 표시
    overlayed_image = np.where(mask[:, :, np.newaxis] > 0, mask_rgb, image)
    
    # 폴리곤 초기화
    polygons = []
    polygon_points = []
    
    # ✅ 디스플레이 갱신
    refresh_display()

def refresh_display():
    """Matplotlib 창을 업데이트하고 확대 상태 유지"""
    global xlim, ylim
    ax.clear()
    ax.imshow(overlayed_image)
    draw_polygon()

    # ✅ 이미지 이름을 제목으로 설정
    image_name = os.path.basename(image_pairs[current_index][0])
    ax.set_title(image_name)

    # ✅ 확대 상태 유지
    if xlim and ylim:
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)

    fig.canvas.draw()

def draw_polygon():
    """현재 점들과 저장된 폴리곤들을 그립니다."""
    for poly_points in polygons:
        poly = Polygon(poly_points, edgecolor='yellow', facecolor='none', lw=2)
        ax.add_patch(poly)
    if len(polygon_points) > 1:
        poly = Polygon(polygon_points, edgecolor='yellow', facecolor='none', lw=2)
        ax.add_patch(poly)
    if polygon_points:
        ax.scatter(*zip(*polygon_points), c='yellow', marker='o')

def on_key(event):
    """키 이벤트 핸들러"""
    global current_index  # 전역 변수 선언
    
    if event.key == 'z':  # 폴리곤 마스크 저장
        save_polygon_mask()
    elif event.key == 'x':  # lets_0pixel 폴더에 저장
        save_to_folder("lets_0pixel")
    elif event.key == 'u':  # 마지막 점 취소
        undo_last_point()
    elif event.key in ['up', 'down', 'left', 'right']:
        move_view(event.key)

def save_polygon_mask():
    """폴리곤 마스크를 저장"""
    global mask, polygon_points, polygons
    if len(polygon_points) > 2:
        cv2.fillPoly(mask, [np.array(polygon_points, dtype=np.int32)], 255)
        polygons.append(polygon_points.copy())  # 폴리곤을 저장
        polygon_points.clear()  # 현재 폴리곤 점 초기화
        refresh_display()

def save_to_folder(folder_name):
    """지정된 폴더에 이미지를 저장하고 PNG 파일도 복사"""
    global current_index  # 전역 변수 선언
    folder_path = os.path.join(D_folder, folder_name)  # D_folder를 기준으로 폴더 생성
    os.makedirs(folder_path, exist_ok=True)
    
    jpg_path, png_path = image_pairs[current_index]
    base_name = os.path.splitext(os.path.basename(jpg_path))[0]
    save_path = os.path.join(folder_path, f"{base_name}_masked.jpg")
    
    # 마스크 영역을 0 픽셀(검은색)으로 변환
    black_masked_image = apply_black_mask(image, mask)
    
    cv2.imwrite(save_path, cv2.cvtColor(black_masked_image, cv2.COLOR_RGB2BGR))
    print(f"✔️ {save_path} 저장 완료!")
    
    # PNG 파일 저장
    mask_save_path = os.path.join(folder_path, f"{base_name}_mask.png")
    cv2.imwrite(mask_save_path, mask)
    print(f"✔️ {mask_save_path} 저장 완료!")
    
    current_index += 1
    load_images()

def undo_last_point():
    """마지막으로 찍은 점을 취소"""
    global polygon_points
    if polygon_points:
        polygon_points.pop()
        refresh_display()

def move_view(direction):
    """이미지 이동"""
    global xlim, ylim
    move_step = 80  # 이동 거리 증가
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
    """마우스 스크롤 이벤트 핸들러"""
    global xlim, ylim
    base_scale = 1.2

    if event.button == 'up':  # 스크롤 업(확대)
        scale_factor = base_scale
    elif event.button == 'down':  # 스크롤 다운(축소)
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

def on_mouse_click(event: MouseEvent):
    """마우스 클릭 이벤트 핸들러"""
    global polygon_points
    if event.xdata is not None and event.ydata is not None:
        polygon_points.append((int(event.xdata), int(event.ydata)))
        refresh_display()

# ✅ Matplotlib 이벤트 핸들러 등록
fig, ax = plt.subplots()
fig.canvas.mpl_connect("button_press_event", on_mouse_click)
fig.canvas.mpl_connect("key_press_event", on_key)
fig.canvas.mpl_connect("scroll_event", on_scroll)

# ✅ 첫 번째 이미지 로드 및 실행
load_images()
plt.show()

