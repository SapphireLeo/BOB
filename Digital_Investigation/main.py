import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', 100)
df = pd.read_csv('./new_dataset.csv')
df.columns = ['website', 'domain', 'ip_address', 'time_captured', 'last_active',
              'crypto_address', 'detected_crypto_type', 'ip_country']

# ip2location.io API에 사용할 url과 GET parameter를 선언합니다.
url = 'https://api.ip2location.io/'
parameters = {'key': '40CE1F061F6526DE11286EB23C600D6C', 'ip': '0.0.0.0'}

# 결과를 저장할 새로운 데이터프레임을 선언합니다.
ip_country = pd.DataFrame(columns=['ip_country'])

for idx in range(len(df.index)):
    parameters['ip'] = df.loc[idx, 'ip_address']
    # api로 HTTP GET method request를 전송합니다.
    response = requests.get(url, params=parameters)
    # 응답 코드가 200일 때만 해당하는 인덱스에 나라 이름 추가합니다. IP주소 결측치는 인덱스가 자동으로 건너뜁니다.
    if response.status_code == 200:
        countryName = requests.get(url, params=parameters).json().get('country_name')
        ip_country.loc[idx] = [countryName]

# api 호출이 끝나면 결과 데이터프레임을 원본에 병합합니다.
df = pd.concat([df, ip_country], axis=1)
# 10000개 데이터에 대한 api 호출이 너무 오래 걸려서(2시간), 새로운 데이터셋으로 저장한 다음 자유롭게 불러올 수 있게 했습니다.
df.to_csv('./new_dataset.csv', index=False)

# 공백을 결측치로 변환합니다.
df.replace(r'^\s*$', np.nan, regex=True, inplace=True)
# 결측치가 포함된 행을 전부 제거하고, 인덱스를 재정렬합니다.
df.dropna(inplace=True)
df.reset_index(drop=True)

# 시간 데이터를 월별로 구분할 수 있기 위해 형식을 datetime으로 변환합니다.
df['time_captured'] = pd.to_datetime(df['time_captured'])
# 최상위 도메인 데이터를 알 수 있도록 별도의 열로 추출합니다.
df['top_level_domain'] = df['domain'].str.split('.').str[-1]


# 사기에 사용된 IP 주소가 가리키는 국가의 종류를 파악합니다.
print(df.value_counts('ip_country'))

# 각 암호화폐의 종류별로 사용된 IP 주소 국가의 분포를 살펴봅니다.
print(df.groupby('detected_crypto_type')['ip_country'].value_counts())


# 각 개월별로 사기에 사용된 암호화폐의 종류를 분석합니다.
monthly_data = df.groupby(pd.Grouper(key='time_captured', freq='M'))['detected_crypto_type']\
    .value_counts()\
    .unstack(fill_value=0)

# 인덱스의 형식을 년/월까지만 표시되게 바꿉니다.
monthly_data.index = monthly_data.index.strftime('%YY %mM')

# 데이터를 그래프로 시각화합니다.
monthly_data.plot(kind='bar', stacked=True)

plt.xlabel('Month')
plt.ylabel('Count')
plt.title('Cryptocurrency types by Month')
plt.legend(title='Cryptocurrency types')
plt.show()


# 각 개월별로 사기에 사용된 IP 주소의 국가의 빈도를 측정합니다.
monthly_data = df.groupby(pd.Grouper(key='time_captured', freq='M'))['ip_country']\
    .value_counts().groupby(level=0).nlargest(5).reset_index(level=0, drop=True)\
    .unstack(fill_value=0)

# 데이터를 누적형 막대그래프로 시각화합니다.
monthly_data.index = monthly_data.index.strftime('%YY %mM')
monthly_data.plot(kind='bar', stacked=True)

plt.xlabel('Month')
plt.ylabel('Count')
plt.title('Country of IP Address Values by Month')
plt.legend(title='Country of IP Address')
plt.show()

# TLD에서 최상위 빈도를 보이는 5개 값을 추출합니다.
tld_head_values = df['top_level_domain'].value_counts().nlargest(5).index.tolist()

# IP 주소에 해당하는 나라에서 최상위 빈도를 보이는 5개 값 추출합니다.
country_head_values = df['ip_country'].value_counts().nlargest(5).index.tolist()

# 최상위 5개 값 각각으로 필터링합니다.
filtered_df = df[df['top_level_domain'].isin(tld_head_values) & df['ip_country'].isin(country_head_values)]

# 각 TLD별로 IP 주소 국가의 빈도 수를 측정합니다.
tld_country = filtered_df.groupby('top_level_domain')['ip_country']\
    .value_counts().unstack(fill_value=0)

# 데이터를 누적형 막대그래프로 시각화합니다.
tld_country.plot(kind='bar', stacked=True)

plt.xlabel('Month')
plt.ylabel('Count')
plt.title('Country of IP Address by TLD')
plt.legend(title='Country of IP Address')
plt.show()
