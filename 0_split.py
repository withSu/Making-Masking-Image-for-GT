import os
import shutil

# 원본 폴더 경로
image_folder = "./datasets/image"
json_folder = "./datasets/json"

# 대상 폴더 경로
output_base = "./datasets/분리"

# 원본 폴더의 파일 목록 가져오기
image_files = sorted(os.listdir(image_folder))
json_files = sorted(os.listdir(json_folder))

# 파일을 10개씩 묶어 새로운 폴더로 복사
batch_size = 10
num_batches = (len(image_files) + batch_size - 1) // batch_size

for i in range(num_batches):
    batch_folder = f"{output_base}{i+1}"
    image_output = os.path.join(batch_folder, "image")
    json_output = os.path.join(batch_folder, "json")
    
    os.makedirs(image_output, exist_ok=True)
    os.makedirs(json_output, exist_ok=True)
    
    # 현재 배치에 해당하는 파일들 선택
    batch_images = image_files[i * batch_size : (i + 1) * batch_size]
    batch_jsons = json_files[i * batch_size : (i + 1) * batch_size]
    
    # 파일 복사
    for file in batch_images:
        shutil.copy2(os.path.join(image_folder, file), os.path.join(image_output, file))
    
    for file in batch_jsons:
        shutil.copy2(os.path.join(json_folder, file), os.path.join(json_output, file))
    
    print(f"{batch_folder}에 {len(batch_images)}개 복사 완료.")
