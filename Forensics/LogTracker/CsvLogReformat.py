import pandas as pd

# read csv file with catching exception.
try:
    log = pd.read_csv('./invalid_src_ip_mac_pair.csv', header=None)
except FileNotFoundError:
    print("file './invalid_src_ip_mac_pair.csv' is not found.")
    exit(-1)

# rename columns.
log.columns = ['timestamp', 'employee_num', 'source_ip', 'source_mac', 'source_port',
               'destination_ip', 'destination_mac', 'destination_port', 'file_size']


# this function convert IP from integer format into string format.
def convert_ip(int_ip_address):
    return '.'.join(map(str, [(int_ip_address & (0xFF << (i * 8))) >> (i * 8) for i in range(3, -1, -1)]))


# this function convert MAC address from integer format into string format.
def convert_mac(int_mac_address):
    return ':'.join(map(lambda x: format(x, '02x'), [(int_mac_address & (0xFF << (i * 8))) >> (i * 8) for i in range(5, -1, -1)]))


# reformat all rows of log file.
for idx in log.index:
    log.loc[idx, 'source_ip'] = convert_ip(log.loc[idx, 'source_ip'])
    log.loc[idx, 'source_mac'] = convert_mac(log.loc[idx, 'source_mac'])
    log.loc[idx, 'destination_ip'] = convert_ip(log.loc[idx, 'destination_ip'])
    log.loc[idx, 'destination_mac'] = convert_mac(log.loc[idx, 'destination_mac'])

# save the reformatted dataframe into csv file.
log.to_csv('./invalid_src_ip_mac_pair(reformatted).csv')
# display success.
print("successfully saved file './invalid_src_ip_mac_pair(reformatted).csv'.")
