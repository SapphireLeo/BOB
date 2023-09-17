# 프레임 하나의 정보를 체계적으로 저장하기 위한 프레임 클래스를 규정한다.
class Frame:
    def __init__(self):
        self.timestamp = None
        self.channel = None
        self.type = None
        self.offset = None
        self.size = None
        self.data = None

    # pymysql의 executemany에 대응하기 위한 튜플을 반환하는 함수를 만든다.
    def into_tuples(self):
        return self.timestamp, self.channel, self.type, self.offset, self.size, self.data


# NAL의 시그니처, 블랙박스 시스템의 시그니처를 상수로 지정한다.
NAL_SIGNATURE = b'\x00\x00\x00\x01'
SYSTEM_SIGNATURE_1 = b'\xDC\xDC\xDC\xDC'
SYSTEM_SIGNATURE_2 = b'\x5A\x5A\x5A'


# 다음으로 등장하는 블랙박스 시스템의 시그니처 코드를 인식하는 함수.
def find_system_signature(video):
    # 시스템의 시그니처 상수 값을 받아온다.
    signature = SYSTEM_SIGNATURE_1

    # queue 데이터 구조의 버퍼로 사용할 5바이트 크기의 바이트 배열을 선언한다.
    buffer = bytearray(5)
    # 1바트씩 읽으면서 버퍼에 push와 pop을 반복하고, 만약 시그니처가 발견될 경우 중단한다.
    while buffer[0:4] != signature or buffer[0:3] == b'\x5A\x5A\x5A':
        buffer.pop(0)
        buffer += video.read(1)

    # 발견된 시그니처의 종류를 반환한다.
    if buffer[0:3] == b'\x5A\x5A\x5A':
        return 'big footer'
    elif buffer[4] == 3:
        return 'footer'
    elif buffer[4] == 1:
        return 'header'
    else:
        return 'unknown'


def parse(video, size):
    # 여러 개의 프레임들을 저장할 리스트를 선언한다.
    frames = []
    unknown_frame_num = 0
    while True:
        # 만약 현재 파일 포인터가 파일의 크기를 벗어났다면 파일을 전부 소모했음을 나타낸다.
        if video.tell() >= size:
            raise EOFError('video file is all consumed.')

        # 다음 시그니처가 발견될 때까지 1바이트씩 읽는 함수 실행.
        signature_type = find_system_signature(video)

        # 다음 프레임의 정보를 저장하기 위한 프레임 객체를 선언한다.
        new_frame = Frame()

        # 만약 발견된 시그나처가 헤더라면 이에 맞추어 적절하게 정보들을 파싱한다.
        # 파싱한 정보들을 하나의 프레임 객체에 저장한 다음 프레임 객체에 배열에 넣는다.
        if signature_type == 'header':
            new_frame.type = 'I' if video.read(1) == b'\x01' else 'P'  # 이 부분이 1이면 I-frame, 0이면 P-frame.
            new_frame.channel = int.from_bytes(video.read(1), 'little')  # 0 = 전면 채널, 1 = 후면 채널.
            video.seek(video.tell() + 1)  # empty
            new_frame.size = int.from_bytes(video.read(4), 'little')
            video.seek(video.tell() + 8)  # 용도를 모르는 공간
            new_frame.offset = video.tell()
            new_frame.data = video.read(new_frame.size)
            frames.append(new_frame)

        # 푸터라면 푸터의 종류에 따라 프레임에 시간 정보만 적용한 다음,
        # pymysql의 executemany가 사용 가능한 배열로 묶어 반환한다.
        elif signature_type == 'footer':
            video.seek(video.tell() + 0x2F) # 구조를 모르는 공간 건너뛰기
            timestamp = int.from_bytes(video.read(4), 'little')  # UNIX epoch time으로 저장된 4바이트를 읽는다.

            # 푸터에서 발견된 시간 정보를 이전에 발견된 모든 프레임들에 각자 적용한다.
            for frame in frames:
                frame.timestamp = timestamp
            # 모든 프레임들을 튜플의 형태로 변환하여 하나의 배열로 묶은 다음 반환한다.
            return unknown_frame_num, [frame.into_tuples() for frame in frames]
        elif signature_type == 'big footer':
            video.seek(video.tell() + 0x28)# 구조를 모르는 공간 건너뛰기
            timestamp = int.from_bytes(video.read(4), 'little')  # UNIX epoch time으로 저장된 4바이트를 읽는다.

            # 푸터에서 발견된 시간 정보를 이전에 발견된 모든 프레임들에 각자 적용한다.
            for frame in frames:
                frame.timestamp = timestamp
            # 모든 프레임들을 튜플의 형태로 변환하여 배열로 묶은 다음 반환한다.
            return unknown_frame_num, [frame.into_tuples() for frame in frames]
        # 만약 알려진 시그니처 이외일 경우, DCDCDCDC는 발견되었지만
        # 그 이후의 숫자가 01 또는 03이 아니라는 뜻이다.
        # 이 경우, 카빙에 필요 없는 데이터로 표시하고 다음 시그니처를 다시 읽는다.
        else:
            unknown_frame_num += 1
            continue
