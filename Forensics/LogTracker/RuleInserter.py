import configparser
import os
import pymysql
import pandas as pd

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
EMPLOYEE_LIST_FILE_DIR = config.get('employee list', 'file_dir')
EMPLOYEE_LIST_FILE_NAME = config.get('employee list', 'file_name')
EMPLOYEE_LIST_FILE_TYPE = config.get('employee list', 'file_type')
EMPLOYEE_LIST_FILE_PATH = EMPLOYEE_LIST_FILE_DIR + EMPLOYEE_LIST_FILE_NAME

SERVER_LIST_FILE_DIR = config.get('server list', 'file_dir')
SERVER_LIST_FILE_NAME = config.get('server list', 'file_name')
SERVER_LIST_FILE_TYPE = config.get('server list', 'file_type')
SERVER_LIST_FILE_PATH = SERVER_LIST_FILE_DIR + SERVER_LIST_FILE_NAME

# read files into pandas dataframe with catching exception.
try:
    employeeList = pd.read_excel(EMPLOYEE_LIST_FILE_PATH,
                                 usecols=range(6))
except FileNotFoundError:
    print(f"fatal error: path of employee list '{EMPLOYEE_LIST_FILE_PATH}' does not exists.")
    exit(-1)
else:
    print("employee list file has found:", EMPLOYEE_LIST_FILE_PATH)

try:
    serverList = pd.read_excel(SERVER_LIST_FILE_PATH,
                               usecols=range(5))
except FileNotFoundError:
    print(f"fatal error: path of server list '{SERVER_LIST_FILE_PATH}' does not exists.")
    exit(-1)
else:
    print("server list file has found:", SERVER_LIST_FILE_PATH)


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
cursor.execute("DROP TABLE IF EXISTS employee;")
cursor.execute("DROP TABLE IF EXISTS server;")

# create employee table and indexes.
sql = """
CREATE TABLE employee (
    num INT UNSIGNED PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    account VARCHAR(50) NOT NULL,
    mac CHAR(17) NOT NULL,
    ip CHAR(15) NOT NULL, 
    region VARCHAR(10) NOT NULL
);
"""
cursor.execute(sql)
cursor.execute("CREATE INDEX employee_access_index on employee(ip, region);")

# create server table.
sql = """
CREATE TABLE server (
    no INT NOT NULL,
    name CHAR(10) NOT NULL,
    ip CHAR(15) NOT NULL,
    mac CHAR(17) NOT NULL,
    port INT UNSIGNED NOT NULL,
    PRIMARY KEY(ip, port)   
);
"""
cursor.execute(sql)
db.commit()

# read pandas dataframe and insert data into database.
for idx in employeeList.index:
    employee_ip_int = 0
    employee_mac_int = 0
    num = employeeList.loc[idx, 'NUM']
    name = employeeList.loc[idx, 'NAME']
    account = employeeList.loc[idx, 'ACCOUNT']
    employee_mac_array = employeeList.loc[idx, 'MAC'].split(':')

    # convert ip/mac address into integer type.
    for byte in employee_mac_array:
        employee_mac_int <<= 8
        employee_mac_int += int(byte, 16)
    employee_ip_array = employeeList.loc[idx, 'IP'].split('.')
    for byte in employee_ip_array:
        employee_ip_int <<= 8
        employee_ip_int += int(byte)

    region = employeeList.loc[idx, 'REGION']
    sql = f"""
    INSERT INTO employee(num, name, account, mac, ip, region)
    VALUES('{num}','{name}','{account}','{employee_mac_int}','{employee_ip_int}','{region}');
    """
    cursor.execute(sql)
    db.commit()
print('inserted employee table successfully.')

for idx in serverList.index:
    server_ip_int = 0
    server_mac_int = 0
    no = serverList.loc[idx, 'No']
    name = serverList.loc[idx, 'Name']
    server_ip_array = serverList.loc[idx, 'IP'].split('.')

    # convert ip/mac address into integer type.
    for byte in server_ip_array:
        server_ip_int <<= 8
        server_ip_int += int(byte)
    server_mac_array = serverList.loc[idx, 'MAC'].split(':')
    for byte in server_mac_array:
        server_mac_int <<= 8
        server_mac_int += int(byte, 16)

    port = serverList.loc[idx, 'PORT']
    sql = f"""
    INSERT INTO server(no, name, ip, mac, port)
    VALUES('{no}','{name}','{server_ip_int}','{server_mac_int}','{port}');
    """
    cursor.execute(sql)
    db.commit()
print('inserted server table successfully.')

# close objects.
cursor.close()
db.close()

