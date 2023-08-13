import configparser
import os
import json
import pymysql
import time

BATCH_QUERY_SIZE = 1000000

# get next word of file.
def get_next_word(text_file):
    word = ''
    while True:
        # read the file byte by byte.
        buffer = text_file.read(1)
        # return word if end of word or file is detected.
        if buffer == ' ' or buffer == '':
            return word
        word += buffer


# this generates batch array for executemany in PyMySQL module.
def generate_batch(text_file, batch_number):
    batch_count = 0
    query_arguments = []
    batch_array = []
    # if batch number is negative or non-integer number,
    # this function would loop forever until reaching EOF.
    while batch_count != batch_number:
        batch_array.clear()
        for _ in range(BATCH_QUERY_SIZE):
            # initiate an query arguments array.
            query_arguments.clear()
            src_ip_int = 0
            src_mac_int = 0
            dest_ip_int = 0
            dest_mac_int = 0

            # get month, day, year.
            month_str = get_next_word(log)
            if month_str == '':
                break
            month = monthConfig.get(month_str)
            day = get_next_word(log)
            year = get_next_word(log)
            get_next_word(log)  # day of the week
            timestamp = get_next_word(log)
            get_next_word(log) # string 'BOB_Forensics'

            # add the timestamp to query argumets list.
            query_arguments.append(f"{year}-{month}-{day} {timestamp}") # timestamp

            # employee number
            query_arguments.append(get_next_word(log))
            # source ip(int). convert ip string into integer format.
            src_ip_array = get_next_word(log).split('.')
            for byte in src_ip_array:
                src_ip_int <<= 8
                src_ip_int += int(byte)
            query_arguments.append(src_ip_int)
            # source mac(int), convert mac string into integer format.
            src_mac_array = get_next_word(log).split(':')
            for byte in src_mac_array:
                src_mac_int <<= 8
                src_mac_int += int(byte, 16)
            query_arguments.append(src_mac_int)
            # source port
            query_arguments.append(get_next_word(log))

            # server name
            get_next_word(log)
            # server ip(int), convert ip string into integer format.
            dest_ip_array = get_next_word(log).split('.')
            for byte in dest_ip_array:
                dest_ip_int <<= 8
                dest_ip_int += int(byte)
            query_arguments.append(dest_ip_int)
            # server mac(int) convert mac string into integer format.
            dest_mac_array = get_next_word(log).split(':')
            for byte in dest_mac_array:
                dest_mac_int <<= 8
                dest_mac_int += int(byte, 16)
            query_arguments.append(dest_mac_int)
            # server port
            query_arguments.append(get_next_word(log))
            # size
            query_arguments.append(get_next_word(log))

            # if current file pointer is not on the end of file,
            # move file pointer backward because there is no newline character.
            if not query_arguments[-1].isdigit() and query_arguments[-1] != '':
                query_arguments[-1] = query_arguments[-1][:-3]
                text_file.seek(text_file.tell() - 4)

            batch_array.append(tuple(query_arguments))

        if len(batch_array) == 0:
            break
        yield batch_array
        batch_count += 1


# get configuration object.
config = configparser.ConfigParser()

# read configuration file with catching exception.
CONFIG_FILE_PATH = os.getcwd() + os.sep + 'config.ini'
try:
    config.read(CONFIG_FILE_PATH, encoding='UTF-8')
except FileNotFoundError:
    print("fatal error: '.config' file(UTF-8) is not in this directory.")
    exit(-1)
else:
    print("config file has found:", CONFIG_FILE_PATH)

# get file path from configuration file.
LOG_FILE_DIR = config.get('log', 'file_dir')
LOG_FILE_NAME = config.get('log', 'file_name')
LOG_FILE_ENCODING = config.get('log', 'encoding')

TIME_FILE_DIR = config.get('time', 'file_dir')
TIME_FILE_NAME = config.get('time', 'file_name')

# read configuration file with catching exception.
with open(TIME_FILE_DIR + TIME_FILE_NAME, "r") as jsonFile:
    try:
        timeConfig = json.load(jsonFile)
    except FileNotFoundError:
        print(f"fatal error: path of log '{TIME_FILE_DIR + TIME_FILE_NAME}' does not exists.")

# get month configuration (ex: Jan = "01")
monthConfig = timeConfig.get('month')

# open log file with catching exception.
try:
    log = open(LOG_FILE_DIR + LOG_FILE_NAME, 'r', encoding=LOG_FILE_ENCODING)
except FileNotFoundError:
    print(f"fatal error: path '{LOG_FILE_DIR + LOG_FILE_NAME}' does not exists.")
    exit(-1)

# get mysql database.
db = pymysql.connect(
    user='root',
    passwd='0914',
    host='localhost',
    charset='utf8'
)

# get cursor from database.
cursor = db.cursor()

# create database and use it.
cursor.execute("CREATE DATABASE IF NOT EXISTS forensics;")
cursor.execute("USE forensics;")

# cursor.execute("DROP TABLE IF EXISTS logs;")
# create logs table.
sql = """
CREATE TABLE logs (
    timestamp datetime,
    employee_num INT UNSIGNED,
    src_ip INT UNSIGNED,
    src_mac BIGINT UNSIGNED,
    src_port INT UNSIGNED,
    dest_ip INT UNSIGNED,
    dest_mac BIGINT UNSIGNED,
    dest_port INT UNSIGNED,
    size INT UNSIGNED
);
"""
cursor.execute(sql)

# create indexes.
cursor.execute("CREATE INDEX time_index on logs(timestamp, employee_num);")
cursor.execute("CREATE INDEX access_index on logs(src_ip, src_mac, dest_port);")

# start measuring time.
startTime = time.time()

# prepare sql query string.
sql = """
INSERT INTO logs(timestamp, employee_num, src_ip, src_mac, src_port, 
    dest_ip, dest_mac, dest_port, size)
VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s);
"""

# generate batch and execute with executemany().
for idx, batch in enumerate(generate_batch(log, -1)):
    cursor.executemany(sql, batch)
    # commit database transaction.
    db.commit()
    # print insertion progress with batch count.
    print(f"DB insertion is ongoing...(chunk number {idx})")


# close objects.
log.close()
cursor.close()
db.close()

# end measuring time and display.
endTime = time.time()
print('time consumed:', endTime - startTime)
