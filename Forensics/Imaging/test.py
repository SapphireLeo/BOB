import datetime

# 주어진 날짜와 시간
dt_str = '2017/08/03 19:26:59'
dt = datetime.datetime.strptime(dt_str, '%Y/%m/%d %H:%M:%S')

# Unix epoch time으로 변환
epoch = int((dt - datetime.datetime(1970, 1, 1)).total_seconds())

print(f"{epoch:X}")