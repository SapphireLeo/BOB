import hashlib
import os
import sys
import pandas as pd
import mysql.connector

CONFIG = {
    'user': "root",
    'password': "0914",
    'host': "localhost",
}
# 쿼리문을 작성하고 동작을 추가합니다.
INIT_QUERIES = list()
# Forensics 데이터베이스가 없다면 추가합니다.
INIT_QUERIES.append("CREATE DATABASE IF NOT EXISTS Forensics;")
# Forensics 데이터베이스를 사용합니다.
INIT_QUERIES.append("USE Forensics;")
# 만약 Hash 테이블이 이미 있다면 삭제합니다.
INIT_QUERIES.append("DROP TABLE IF EXISTS Hash;")
# Hash 테이블을 생성합니다.
INIT_QUERIES.append("""
CREATE TABLE Hash(
    file_name VARCHAR(255) PRIMARY KEY,
    hash_value BINARY(16) NOT NULL
);
""")

# mysql 서버에 연결한 다음 connector 객체를 반환하는 함수
def connect_mysql():
    return mysql.connector.connect(**CONFIG)


# connector 객체와 cursor 객체를 입력받아 쿼리를 실행하는 함수
def mysql_run_queries(connection, cursor, queries):
    try:
        # 쿼리는 리스트 또는 튜플이어야 합니다. 쿼리를 차례로 실행하고 커밋합니다.
        for query in queries:
            cursor.execute(query)
            connection.commit()
    # mysql 에러가 발생했을 경우 작업을 중단하고 에러 메시지를 출력합니다.
    except mysql.connector.Error as err:
        connection.rollback()
        print(f"Error Occurred: {err}")

# mysql 데이터베이스 초기화 쿼리를 실행합니다.
def mysql_init(connection, cursor):
    mysql_run_queries(connection, cursor, INIT_QUERIES)

# 지정한 파일을 읽어서 md5 해시값을 계산하여 반환하는 함수입니다.
def calculate_md5(file_path):
    md5_hash = hashlib.md5()  # 해시 알고리즘 선택합니다. (여기서는 md-5을 사용)

    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


# 지정한 디렉토리의 하위 파일과 디렉토리를 재귀적으로 모두 검색하여 해시값을 반환하는 함수입니다.
def calculate_md5_for_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 현재 디렉토리의 절대경로에 파일의 상대경로를 결합해서 절대경로를 만듭니다.
            file_path = os.path.join(root, file)
            try:
                # 파일 크기를 계산한 다음, 파일의 크기가 1GB 이하인 경우만 계산합니다.
                file_size = os.path.getsize(file_path)
                if file_size < 1024 * 1024 * 1024:
                    md5_hash = calculate_md5(file_path)
                    # 파일 경로가 지나치게 상위일 경우에 대비해, 제너레이터 방식으로 값을 반환합니다.
                    yield file_path, md5_hash
                else:
                    print(f'Error: File "{file_path}" is bigger than 1GB.')
            # 권한 문제로 접근이 불가능할 경우 에러를 출력합니다.
            except PermissionError:
                print(f'Error: There is no permission to access file "{file_path}".')
            # CLI 환경에서 구분을 위한 줄을 출력합니다.
            print('-' * 40)

def main():
    # File과 Hash 두 컬럼을 가진 데이터프레임을 생성합니다.
    result_dataset = pd.DataFrame(columns=['File', 'Hash'])

    # 명령 인자가 올바르게 입력되지 않았을 경우 오류를 출력합니다.
    if len(sys.argv) != 2:
        print('Fatal error: wrong arguments. Insert only one file directory name for arguments.')
        exit(-1)

    # connector 정보를 받아오고, connector에서 cursor 정보도 받아옵니다.
    connection = connect_mysql()
    cursor = connection.cursor()

    # mysql 테이블을 초기화합니다.
    mysql_init(connection, cursor)

    # 첫 번째 명령 인자를 경로로 저장합니다.
    directory_path = sys.argv[1]

    # 위의 함수를 이용하여 파일 경로 정보와 해당 파일의 md5 해시값을 출력합니다.
    for file_path, md5_hash in calculate_md5_for_directory(directory_path):
        print(f'File: {file_path}')
        print(f'MD5 hash: {md5_hash}')
        result_dataset.loc[len(result_dataset.index)] = [file_path, md5_hash]
        queries = [f"INSERT INTO Hash (file_name, hash_value) VALUES ('{file_path}', X'{md5_hash}');"]
        mysql_run_queries(connection, cursor, queries)

    # 결과를 csv 파일로 저장합니다.
    result_dataset.to_csv('./md5_hash_result.csv')


if __name__ == "__main__":
    main()

