# Image Masking and Annotation Tool

This project provides tools for applying masks and annotations to images using Python and OpenCV. The main scripts are `prepare-labeling.py` and `0pixel_ver0.3.py`.

## Features

- **Image Masking**: Apply and save masks on images.
- **Polygon Annotation**: Create and edit polygon annotations on images.
- **Navigation**: Use keyboard and mouse controls to navigate and manipulate images.

## Requirements

- Python 3.x
- OpenCV
- NumPy
- Matplotlib

Install the required packages using pip:

pip install opencv-python numpy matplotlib

## Usage

### prepare-labeling.py

- **Draw Polygons**: Click to create points and form polygons.
- **Save Mask**: Press `z` to save the current polygon as a mask.
- **Navigate Images**: Press `x` to save and move to the next image.
- **Undo Last Point**: Press `u` to undo the last point.
- **Image Navigation**: Use arrow keys to move and scroll to zoom.

Run the script:

```
python prepare-labeling.py
```

### 0pixel_ver0.3.py

- **Load Annotations**: Load existing annotations from JSON files.
- **Draw Shapes**: Draw rectangles and polygons based on annotations.
- **Zoom and Pan**: Use mouse scroll to zoom and drag to pan.

Run the script:

```
python 0pixel_ver0.3.py
```

## Directory Structure

- `datasets/1/image/`: Directory for JPG images.
- `datasets/1/mask/`: Directory for PNG masks.
- `datasets/1/visual/`: Directory for saved masked images.
- `datasets/1/0pixel/`: Directory for images with 0-pixel masks.

## Contributing

Feel free to submit issues or pull requests for suggestions or improvements.

## License

This project is licensed under the MIT License.

---

# 이미지 마스킹 및 주석 도구

이 프로젝트는 Python과 OpenCV를 사용하여 이미지에 마스크와 주석을 적용할 수 있는 도구를 제공합니다. 주요 스크립트는 `prepare-labeling.py`와 `0pixel_ver0.3.py`입니다.

## 기능

- **이미지 마스킹**: 이미지에 마스크를 적용하고 저장
- **폴리곤 주석**: 이미지에 폴리곤 주석 생성 및 편집
- **내비게이션**: 키보드와 마우스를 사용하여 이미지 탐색 및 조작

## 요구 사항

- Python 3.x
- OpenCV
- NumPy
- Matplotlib

필요한 패키지는 다음 명령어로 설치할 수 있습니다:

```
pip install opencv-python numpy matplotlib
```

## 사용법

### prepare-labeling.py

- **폴리곤 그리기**: 클릭하여 점을 생성하고 폴리곤을 형성
- **마스크 저장**: `z` 키를 눌러 현재 폴리곤을 마스크로 저장
- **이미지 탐색**: `x` 키를 눌러 저장하고 다음 이미지로 이동
- **마지막 점 취소**: `u` 키를 눌러 마지막 점 취소
- **이미지 내비게이션**: 방향키로 이동하고 스크롤로 확대/축소

스크립트 실행:

```
python prepare-labeling.py
```

### 0pixel_ver0.3.py

- **주석 불러오기**: JSON 파일에서 기존 주석 불러오기
- **도형 그리기**: 주석을 기반으로 사각형과 폴리곤 그리기
- **확대 및 이동**: 마우스 스크롤로 확대하고 드래그하여 이동

스크립트 실행:

```
python 0pixel_ver0.3.py
```

## 디렉토리 구조

- `datasets/1/image/`: JPG 이미지 디렉토리
- `datasets/1/mask/`: PNG 마스크 디렉토리
- `datasets/1/visual/`: 마스크가 적용된 이미지 저장 디렉토리
- `datasets/1/0pixel/`: 0픽셀 마스크가 적용된 이미지 저장 디렉토리

## 기여

제안이나 개선 사항이 있으면 이슈나 풀 리퀘스트를 제출해 주세요.

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다.
