import pyewf
import hashlib


def create_e01_image(source_path, output_path):
    ewf_handle = pyewf.handle()
    ewf_handle.open(source_path)

    hash_object = hashlib.sha256()

    with open(output_path, 'wb') as f:
        for chunk in ewf_handle.iterate():
            f.write(chunk)
            hash_object.update(chunk)

    ewf_handle.close()
    hash_value = hash_object.hexdigest()
    print("Image Hash:", hash_value)


# 사용 예시
source_path = 'D:/'  # 이미징할 디스크 파일 경로로 수정
output_path = './output_image.E01'  # 생성될 E01 이미지 파일 경로로 수정

create_e01_image(source_path, output_path)
