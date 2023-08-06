import tracemalloc

def your_function_to_profile():
    # 여기에 메모리를 추적하고자 하는 함수를 작성합니다.
    # 예를 들어, 다음과 같은 코드를 메모리를 측정하려는 함수로 대체해주세요.
    my_list = [i for i in range(1000000)]
    return my_list

# if __name__ == "__main__":
tracemalloc.start()  # 메모리 추적 시작

# 함수 호출
result = your_function_to_profile()

current, peak = tracemalloc.get_traced_memory()  # 현재 메모리 사용량 및 최대 메모리 사용량 확인

print(f"Current memory usage: {current / 10**6} MB")  # MB 단위로 출력
print(f"Peak memory usage: {peak / 10**6} MB")  # MB 단위로 출력

tracemalloc.stop()  # 메모리 추적 중지