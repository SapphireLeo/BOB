import requests
import pandas as pd
import numpy as np

# 새 파일의 경로와 읽어들일 원래 파일의 경로를 선언합니다.
NEW_FILE_PATH = "./prepared_exif_metadata.csv"
ORIGINAL_FILE_PATH = r"C:\Users\Sapphire\Documents\BoB\Digital_Forensics\분석기법(유현)\JohnDoe\EXIF Metadata 20230727015502.csv"

# API에 사용할 url과 GET parameter를 선언합니다.
url = 'https://maps.googleapis.com/maps/api/geocode/json'
# 사용한 API KEY입니다.
API_KEY = "AIzaSyASbWkCO8xFGSzYT44Xq4HHqZyE1Zv84Dk"
parameters = {
    'latlng': '37.4858861, 127.104125',
    'language': 'ko',
    'key': API_KEY,
}


def get_location(dataframe):
    location_dataframe = pd.DataFrame(columns=['Location'])
    for i in range(len(dataframe)):
        latitude, longitude = dataframe.loc[i, 'Latitude'], dataframe.loc[i, 'Longitude']
        parameters['latlng'] = str(latitude) + ', ' + str(longitude)

        response = requests.get(url, params=parameters)

        # 응답 코드가 200일 때만 응답에서 주소를 읽어서 저장합니다.
        if response.status_code == 200:
            location = response.json().get('results')[0].get('formatted_address')
            location_dataframe.loc[i] = [location]

        print(f'Getting location address from Google Geo server...({i / len(dataframe) * 100:6.2f}%)')

    print('Getting location address from Google Geo server...(100.00%)')
    dataframe = pd.concat([dataframe, location_dataframe], axis=1)

    return dataframe


# 목표하는 정보가 있는 파일이 있을 경우 그 파일의 정보를 읽어서 출력하고, 그렇지 않을 경우 기존 파일에서 정보를 읽는 함수입니다.
def data_preparation(new_file_path, original_file_path):
    try:
        metadata = pd.read_csv(new_file_path)
        # 목표하는 파일 이름이 있으며, dataframe 형식으로 읽을 수 있고 Location 컬럼도 있다면 바로 반환합니다.
        if 'Location' in metadata.columns:
            pass
        # 만약 파일은 있지만 Location 컬럼이 없다면 밑의 오류 처리문으로 넘어갑니다.
        else:
            print("Target file has no prepared column 'Location'. Creating new one...")
            raise FileNotFoundError

    # 해당하는 파일이 없다면 새로운 파일을 생성합니다.
    except FileNotFoundError:
        # 기존 csv 파일을 읽습니다.
        before_preparation = pd.read_csv(original_file_path)
        # 빈 열과 필요 없는 열을 모두 제거합니다.
        before_preparation.dropna(axis=1, how='all', inplace=True)
        before_preparation.drop(['Source Type', 'Score', 'File Path', 'Path', 'Size'], axis=1, inplace=True)

        # 비어 있는 데이터를 모두 결측치(NaN)으로 전환합니다.
        before_preparation.loc[before_preparation['Device Model'].isnull(), ['Latitude', 'Longitude', 'Altitude']] = np.nan

        # 만약 데이터가 이미 있지 않을 경우, 메타데이터를 다시 준비하여 UTF-8(BOM) 형태로 저장합니다.
        metadata = get_location(before_preparation)

        # 시간대 정보를 지웁니다.
        metadata['Date Created'] = metadata['Date Created'].str.replace('KST', '', regex=True)
        # 생성 시간을 datetime 속성으로 변경 후 서울 시간으로 변환합니다.
        metadata['Date Created'] = pd.to_datetime(metadata['Date Created']) - pd.Timedelta(hours=9)

        metadata.to_csv(NEW_FILE_PATH, index=False, encoding='utf-8-sig')
    return metadata


# 준비된 함수를 실행합니다.
def main():
    metadata = data_preparation(NEW_FILE_PATH, ORIGINAL_FILE_PATH)
    metadata.drop(['Latitude', 'Longitude', 'Altitude', 'Device Model', 'Device Make'], inplace=True)

if __name__ == "__main__":
    main()
