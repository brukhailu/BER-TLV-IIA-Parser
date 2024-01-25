import sys
import logging
from datetime import datetime

now = datetime.now()
date_log = now.strftime("%d%m%Y")
# Configure logging to write to a log file
logging.basicConfig(filename=f'{date_log}.log', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_write(*args, **kwargs):
    log_entry = ' '.join(map(str, args))
    # log_entry_with_datetime = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {log_entry}"
    logging.info(log_entry)

# Redirect sys.stdout to the log file
sys.stdout = open(date_log + '.log', 'a')

def check_mandatory_fields_for_header(data):
    mandatory_fields = {
        'FF45': 'Application File Header',
        'FF49': 'File Header Block',
        'DF805D': 'File Sequence Number',
        'DF807D': 'File Type',
        'DF807C': 'File Date',
        'DF8079': 'Institution Number',
        'DF807A': 'Agent Code'
    }
    missing_fields = []
    for key, value in mandatory_fields.items():
        if key not in data:
            missing_fields.append(f"'{key}': '{value}")

    if missing_fields:
        i = 0
        log_write('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        log_write("                Missed Mandatory Tags In The Header")
        for field in missing_fields:
            i += 1
            log_write("!!!!!!!!!! "+ str(i) +". " +field)
    else:
        pass

def check_mandatory_fields_for_trailer(data):
    mandatory_fields = {
        'FF46':'Application File Trailer',
        'FF4A':'File Trailer Block',
        'DF807E':'Number of records',
        'DF805D':'File Sequence Number'
    }
    missing_fields = []
    for key, value in mandatory_fields.items():
        if key not in data:
            missing_fields.append(f"'{key}': '{value}")

    if missing_fields:
        i = 0
        log_write('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        log_write("                Missed Mandatory Trailer Tags In The Header")
        for field in missing_fields:
            i += 1
            log_write("!!!!!!!!!! "+ str(i) +". " +field)
    else:
        pass
def get_length_value(data, initial):
    index = 0
    length_hex, length, value = 'N/A', 'N/A', 'N/A'
    length_hex = data[initial:initial + 2]
    actual_value = '0'
    if length_hex.startswith('8'):
        length_hex = data[initial + 1 :initial + 4]
        length = int(length_hex, 16)
        if length >127:
            log_write("!!!!! The length value should be 2 Byte, since it's >127")
        value = data[initial + 4 :initial + 4+ length]
        actual_value = data[initial + 5 :]
        # if length != len(value):
        #     log_write()(" !!!!! Length of expected value & actual value is different. Expected = " + str(length), "Actual = " + str(len(value)))
    else:
        length = int(length_hex, 16)
        value = data[initial + 2:initial + 2 + length]
        actual_value = data[initial + 2:]
    if length != len(value):
        log_write(" !!!!! Length of expected value & actual value is different. Expected = " + str(length), "Actual = " + str(len(value)))
    elif length != len(actual_value) and data.startswith('FF45'):
        log_write(" !!!!! Length of expected value & actual value is different. Expected = " + str(length), "Actual = " + str(len(actual_value)))
    return length_hex, length, value

def parse_and_get_left_data(data, startwith, value_end, tag_message, error_message, spacing):
    tag = data[0:value_end]
    value_left = ''
    value = ''
    log_write(spacing + data)
    if data.startswith(startwith):
        value_length = get_length_value(data, value_end)
        length_hex = value_length[0]
        length = value_length[1]
        value = value_length[2]
        log_write(spacing + tag_message)
        log_write(spacing + "T => " + tag)
        log_write(spacing + "L => " + str(length_hex) + ", " + str(length))
        log_write(spacing + "V => " + str(value))

        value_left = data[value_end + len(length_hex) + length:]  # value after the sequence number
    else:
        log_write(tag + " => " + error_message)
    if tag == 'FF45' or tag == 'FF49' or tag =='FF46' or tag == 'FF4A':
        value_left = value
    return value_left

def parse_file_header_trailer_block(data, desciption, spacing=""):
    result = {}
    i = 0
    formatted_output = ""
    while i < len(data):
        tag = data[i:i + 6]
        i += 6
        if data[i] == '8':
            length_hex = data[i:i + 3]
            i += 3
        else:
            length_hex = data[i:i + 2]
            i += 2
            if int(length_hex, 16) > 127:
                log_write(" !!!!! The length value should be 2 Byte, since it's >127")
        length_decimal = int(length_hex, 16)
        value = data[i:i + length_decimal]
        i += length_decimal

        result[tag] = {
            'Tag': tag,
            'Length (Hex)': length_hex,
            'Length (Decimal)': length_decimal,
            'Value': value
        }
        if desciption == 'header':
            desciption = get_description_of_file_header
        elif desciption == 'trailer':
            desciption = get_description_of_file_trailer
        # Format the output
        log_write(f"{spacing} {data[i:]}")
        log_write(f"{spacing} {tag} - {desciption(tag)}")
        log_write(f"{spacing} T => {tag}")
        log_write(f"{spacing} L => {length_hex}, {length_decimal}")
        log_write(f"{spacing} V => {value}")
    # return formatted_output

def get_description_of_file_header(tag):
    descriptions = {
        'DF805D': 'Sequence Number X M',
        'DF807D': 'File Type X M',
        'DF807C': 'File Date X M',
        'DF8079': 'Institution Number X M',
        'DF807A': 'Agent Code X M'
    }
    return descriptions.get(tag, '!!!!! Unknown')

def get_description_of_file_trailer(tag):
    descriptions = {
        'DF805D': 'Sequence Number X M',
        'DF807E': 'Number of records X M',
        'DF8060': 'CRC X O'
    }
    return descriptions.get(tag, '!!!!! Unknown')
def parse_header(data):
    if len(data) > 0:
        check_mandatory_fields_for_header(data)
        #1. Interface File Format (Header)
        application_file_header = parse_and_get_left_data(data, 'FF45', 4,
                                                          'FF45 – Application File Header X M',
                                                          'Unknown Application File Header',
                                                          " ")
        #1.1. FF45 – Application File Header - Sequence Number
        value_after_sequence_no = parse_and_get_left_data(application_file_header, 'DF805D', 6,
                                                          'Sequence Number For Application File Header X M',
                                                          'Unknown Sequence Format for FF49 – File Header Block/ tag DF805D is expected',
                                                          "       ")
        #1.1.1.FF49 – File Header Block
        file_header_block = parse_and_get_left_data(value_after_sequence_no, 'FF49', 4, 'FF49 – File Header Block X M',
                                'Unknown File Header Block', "           ")
        parse_file_header_trailer_block(file_header_block, 'header', "            ")

def parse_trailer(data):
    if len(data) > 0:
        check_mandatory_fields_for_trailer(data)
        application_file_trailer = parse_and_get_left_data(data, 'FF46', 4,
                                                          'FF46 – Application File Trailer X M',
                                                          'Unknown Application File Trailer',
                                                          " ")
        trailer_value_after_sequence_no = parse_and_get_left_data(application_file_trailer, 'DF805D', 6,
                                                          'Sequence Number For Application File Trailer X M',
                                                          'Unknown Sequence Format for FF4A – File Trailer Block/ tag DF805D is expected',
                                                          "       ")
        file_trailer_block = parse_and_get_left_data(trailer_value_after_sequence_no, 'FF4A', 4, 'FF4A – File Trailer Block X M',
                                'Unknown File Trailer Block', "           ")
        parse_file_header_trailer_block(file_trailer_block, 'trailer', "              ")


data = "FF455BDF805D011FF494CDF805D012DF807D07FTYPIIADF807C1319.09.2023_00:00:00DF8079040030DF807A0513075"
#log_write("Designed By Bruk Hailu")
log_write('File Header Start ------------------------------------------------------------------------')
parse_header(data)
log_write('File Header End ----------------------------------------------------------------------------\n')

log_write('File Trailer Start -------------------------------------------------------------------------')
data2 = "FF4623DF805D011FF4A14DF805D012DF807E03151"
parse_trailer(data2)
log_write('File Trailer End -------------------------------------------------------------------------\n')

# Close the redirected output file
sys.stdout.close()

# Reset sys.stdout to the original value (usually the console)
sys.stdout = sys.__stdout__