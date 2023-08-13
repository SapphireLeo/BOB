import configparser
import os
import pymysql
from pymysql.cursors import SSCursor

from Parser import *

# 설정 파일을 읽기 위한 configParser 객체를 선언한다.
config = configparser.ConfigParser()

# 현재 파일의 경로에서 config.ini 파일을 읽기 위한 절대경로를 생성한다.
CONFIG_FILE_PATH = os.getcwd() + os.sep + 'config.ini'

try:
    # 생성된 절대경로를 기반으로 설정 파일을 읽는다. 기본 인코딩 방식은 UTF-8.
    config.read(CONFIG_FILE_PATH, encoding='UTF-8')
except FileNotFoundError:
    # 만약 설정 파일이 없을 경우 오류 메시지와 함께 종료.
    print("fatal error: '.config' file(UTF-8) is not in this directory.")
    exit(-1)
else:
    print("config file has found:", CONFIG_FILE_PATH)

# 설정 파일에서 비디오 파일의 경로를 읽는다.
CONFIG_FILE_PATH = config.get('video file', 'dir') + config.get('video file', 'name')

# 설정 파일에서 데이터베이스와 테이블의 이릉을 읽는다.
DB_NAME = config.get('database', 'name')
TABLE_NAME = config.get('table', 'name')

# pymysql을 사용하여 mysql 데이터베이스에 연결한다. 관련 정보는 설정 파일에서 읽는다.
connection = pymysql.connect(
    user=config.get('database', 'user'),
    passwd=config.get('database', 'password'),
    host=config.get('database', 'host'),
    charset=config.get('database', 'charset'),
    # 커서에서 읽어들인 데이터베이스의 결과가 아주 클 수 있으므로, Server-Side 커서를 만든다.
    cursorclass=SSCursor
)

# 바이너리 모드로 파일을 열고, 파일이 없을 경우 오류 메시지와 함께 종료한다.
try:
    video = open(CONFIG_FILE_PATH, 'rb')
    video_size = os.path.getsize(CONFIG_FILE_PATH)
except FileNotFoundError:
    print(f"fatal error: file '{CONFIG_FILE_PATH}' does not exists.")
    exit(-1)
else:
    print("video file has found:", CONFIG_FILE_PATH)

# 설정 파일에서 각각 채널 0번과 채널 1번에 해당하는 경로에 파일을 바이너리 쓰기 모드로 연다.
channel = [open(config.get('channel 0', 'dir') + config.get('channel 0', 'name'), 'wb')]
channel += [open(config.get('channel 1', 'dir') + config.get('channel 1', 'name'), 'wb')]

# 현재 데이터베이스 연결에서 커서 객체를 생성한다.
cursor = connection.cursor()

# 데이터베이스를 USE하고(없다면 생성한다), 테이블이 존재한다면 드랍한다.
cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME};")
cursor.execute(f"USE {DB_NAME};")
cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME};")

# 테이블을 생성한다.
sql = f"""
CREATE TABLE {TABLE_NAME} (
    num INT UNSIGNED AUTO_INCREMENT,
    timestamp DATETIME NOT NULL,
    channel TINYINT NOT NULL,
    frame_type CHAR(1) NOT NULL,
    offset BIGINT NOT NULL,
    size MEDIUMINT NOT NULL,
    data MEDIUMBLOB NOT NULL,
    CONSTRAINT align PRIMARY KEY(num, timestamp)
);
"""

# 테이블에서 frame type으로 인덱스를 생성한다.
cursor.execute(sql)
cursor.execute(f"CREATE INDEX type_index on {TABLE_NAME}(frame_type);")

# INSERT SQL문을 준비한다.
insertSQL = f"""
INSERT INTO {TABLE_NAME}(timestamp, channel, frame_type, offset, size, data)
VALUES (FROM_UNIXTIME(%s), %s, %s, %s, %s, %s);
"""

# 현재 비디오의 바이트 크기를 출력한다.
print(f"Video Size: {video_size}(0x{video_size:08X}) Bytes")

# 비디오에서 데이터를 카빙하다가 만약 파일의 끝에 도달하였을 경우 카빙을 중단한다.
try:
    totalFrameNum = 0
    while True:
        # 카빙된 데이터는 튜플들의 리스트로 이루어져 있다. 이 데이터를 executemany로 전부 입력한 후 커밋한다.
        carvedData = parse(video, video_size)
        cursor.executemany(insertSQL, carvedData)
        connection.commit()

        # 추출된 프레임의 개수를 더한다.
        totalFrameNum += len(carvedData)

        # 몇 번째 시간 패키지인지를 출력한다.
        print(f'total {totalFrameNum} frames at {video.tell():08X} carved!')
except EOFError as e:
    print(e)
    print('\nfile carving and database insertion is completed.')


# select SQL문을 준비한다.
selectSQL = f"""
SELECT channel, data FROM {TABLE_NAME}
ORDER BY timestamp, num
"""

# SELECT SQL을 실행하고, 결과를 읽는다. 그 후 채널별로 구분하여 파일에 쓴다.
cursor.execute(selectSQL)
for row in cursor:
    channel[row[0]].write(row[1])

# 모든 파일을 닫는다.
cursor.close()
connection.close()
video.close()
channel[0].close()
channel[1].close()


