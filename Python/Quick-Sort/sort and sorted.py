import random
import timeit
import tracemalloc

# 세 개의 파일을 새롭게 만들고, 100만개의 정수를 각각 정방향, 역방향, 무작위로 생성하는 함수입니다.
def file_creation():
    # 세 개의 파일을 엽니다.
    ascending_numbers_file = open('./ascending.txt', 'w')
    descending_numbers_file = open('./descending.txt', 'w')
    randomized_numbers_file = open('./randomized.txt', 'w')

    # 정수를 각각 정방향, 역방향, 무작위로 생성하고 저장합니다.
    for inc, dec in zip(range(0, 10 ** 6), range(10 ** 6 - 1, -1, -1)):
        ascending_numbers_file.write(str(inc) + '\n')
        descending_numbers_file.write(str(dec) + '\n')
        randomized_numbers_file.write(str(random.randrange(0, 10 ** 6)) + '\n')
        # 파일 저장의 진행 상황을 10%마다 출력합니다.
        if inc % (10 ** 4) == 0:
            print(f'writing file...({inc / (10 ** 4): 5.1f}%)', end='\r')

    # 파일 작성이 완료되었음을 출력하고 파일을 닫습니다.
    print(f'writing file...(100%)')
    ascending_numbers_file.close()
    descending_numbers_file.close()
    randomized_numbers_file.close()

# 파일을 열고 그 파일 객체를 반환하는 함수입니다.
def file_open():
    ascending_numbers_file = open('./ascending.txt', 'r')
    descending_numbers_file = open('./descending.txt', 'r')
    randomized_numbers_file = open('./randomized.txt', 'r')
    return ascending_numbers_file, descending_numbers_file, randomized_numbers_file


# 퀵 정렬을 수행하는 함수입니다. 제자리 정렬로 구현되어 있으며, 배열을 반환하지 않고 참조해서 직접 바꿉니다.

def just_sort(array):
    # 입력받은 객체 리스트의 형태가 아닐 경우 예외를 호출합니다.
    if not isinstance(array, list):
        raise TypeError('sorting array must be type of python list, got', type(array), array)
    array.sort()

def just_sorted(array):
    # 입력받은 객체 리스트의 형태가 아닐 경우 예외를 호출합니다.
    if not isinstance(array, list):
        raise TypeError('sorting array must be type of python list, got', type(array), array)
    return sorted(array)

# 문자열의 끝의 개행 문자를 제거하고 정수로 변환해 주는 함수입니다.
def convert(strings):
    return int(strings.strip())


# 먼저 파일 열기를 시도하고, 해당하는 파일이 없을 경우 새로운 파일을 생성해서 엽니다.
try:
    ascendingNumbersFile, descendingNumbersFile, randomizedNumbersFile = file_open()
    print('files are opened!')
except FileNotFoundError:
    print('there is not enough file of numbers for sorting. now creating them...')
    file_creation()
    print('files are created!')
    ascendingNumbersFile = open('./ascending.txt', 'r')
    descendingNumbersFile = open('./descending.txt', 'r')
    randomizedNumbersFile = open('./randomized.txt', 'r')

# 파일을 읽어들인 다음 파일로 저장되어 있는 정수들을 리스트로 저장합니다.
ascending = list(map(convert, ascendingNumbersFile.readlines()))
descending = list(map(convert, descendingNumbersFile.readlines()))
randomized = list(map(convert, randomizedNumbersFile.readlines()))

# 파일을 모두 닫습니다.
ascendingNumbersFile.close()
descendingNumbersFile.close()
randomizedNumbersFile.close()

# 세 개의 배열을 각각 퀵 정렬하면서 timeit 모듈로 실행 시간을 측정합니다.

def avg(array):
    return sum(array) / len(array)

# 정방향 배열을 정렬합니다.
sortTimeConsumed = []
sortedTimeConsumed = []
print('정방향 배열을 정렬 중입니다...')
for i in range(100):
    copied = ascending.copy()
    sortTimeConsumed.append(timeit.timeit('just_sort(copied)', globals=globals(), number=1))
    sortedTimeConsumed.append(timeit.timeit('just_sorted(copied)', globals=globals(), number=1))

tracemalloc.start()
just_sort(ascending)
sort_current, sort_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
new_array1 = just_sorted(ascending)
sorted_current, sorted_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print('정방향 배열의 정렬이 완료되었습니다.')
print('sort 메소드의 정렬 시간:', avg(sortTimeConsumed))
print('sort 메소드에 사용된 메모리:', sort_peak - sort_current)
print('sorted 함수의 정렬 시간:', avg(sortedTimeConsumed))
print('sorted 함수에 사용된 메모리:', sorted_peak - sorted_current)

sortTimeConsumed.clear()
sortedTimeConsumed.clear()
# 역방향 배열을 정렬합니다.
print('\n역방향 배열을 정렬 중입니다...')
for i in range(100):
    copied = descending.copy()
    sortTimeConsumed.append(timeit.timeit('just_sort(copied)', globals=globals(), number=1))
    sortedTimeConsumed.append(timeit.timeit('just_sorted(copied)', globals=globals(), number=1))

tracemalloc.start()
just_sort(descending)
sort_current, sort_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
new_array2 = just_sorted(descending)
sorted_current, sorted_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print('역방향 배열의 정렬이 완료되었습니다.')
print('sort 메소드의 정렬 시간:', avg(sortTimeConsumed))
print('sort 메소드에 사용된 메모리:', sort_peak - sort_current)
print('sorted 함수의 정렬 시간:', avg(sortedTimeConsumed))
print('sorted 함수에 사용된 메모리:', sorted_peak - sorted_current)

sortTimeConsumed.clear()
sortedTimeConsumed.clear()
# 무작위 배열을 정렬합니다.
print('\n무작위 배열을 정렬 중입니다...')
for i in range(100):
    copied = randomized.copy()
    sortTimeConsumed.append(timeit.timeit('just_sort(copied)', globals=globals(), number=1))
    sortedTimeConsumed.append(timeit.timeit('just_sorted(copied)', globals=globals(), number=1))

tracemalloc.start()
just_sort(randomized)
sort_current, sort_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

tracemalloc.start()
new_array3 = just_sorted(randomized)
sorted_current, sorted_peak = tracemalloc.get_traced_memory()
tracemalloc.stop()
print('무작위 배열의 정렬이 완료되었습니다.')
print('sort 메소드의 정렬 시간:', avg(sortTimeConsumed))
print('sort 메소드에 사용된 메모리:', sort_peak - sort_current)
print('sorted 함수의 정렬 시간:', avg(sortedTimeConsumed))
print('sorted 함수에 사용된 메모리:', sorted_peak - sorted_current)

# 정렬된 배열을 저장하기 위한 새로운 파일을 엽니다.
ascendingSortedFile = open('./ascending(sorted).txt', 'w')
descendingSortedFile = open('./descending(sorted).txt', 'w')
randomizedSortedFile = open('./randomized(sorted).txt', 'w')

# 열린 파일에 세 개의 배열을 각각 저장합니다.
for i, (num1, num2, num3) in enumerate(zip(ascending, descending, randomized)):
    ascendingSortedFile.write(str(num1) + '\n')
    descendingSortedFile.write(str(num2) + '\n')
    randomizedSortedFile.write(str(num3) + '\n')
    # 파일 저장의 진행 상황을 10%마다 출력합니다.
    if i % (10 ** 5) == 0:
        print(f'writing sorted file...({int(i / (10 ** 5)): 3d}%)', end='\r')

# 저장이 완료되었음을 출력하고 모든 파일을 닫습니다.
print(f'writing sorted file...(100%)')
ascendingSortedFile.close()
descendingSortedFile.close()
randomizedSortedFile.close()