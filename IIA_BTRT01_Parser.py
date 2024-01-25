# -*- coding: utf-8 -*-
# 3. Interface File Format Record Layout Definition
# Cardholder Application BTRT01
# 3.1. FFFF01 – Cardholder Application BTRT01
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from tkinter import ttk, scrolledtext
import os
import subprocess
import sys
import logging
from datetime import datetime

now = datetime.now()
date_log = now.strftime("%ds%m%Y")
# Configure logging to write to a log file
logging.basicConfig(filename=f'Parsed_Result', level=logging.INFO, format='%(message)s')
# logging.basicConfig(filename=f'Parsed_Result', level=logging.INFO, format='%(asctime)s - %(message)s')

def log_write(*args, **kwargs):
    log_entry = ' '.join(map(str, args))
    # log_entry_with_datetime = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {log_entry}"
    logging.info(log_entry)

def clear_log_file():
    with open('Parsed_Result', 'w') as log_file:
        log_file.write("")  # This will clear the content of the file

# Call the clear_log_file function to clear the log file before logging

# Redirect sys.stdout to the log file
sys.stdout = open('Parsed_Result', 'a')
def get_length_value(data, initial):
    index = 0
    length_hex, length, value = 'N/A', 'N/A', 'N/A'
    length_hex = data[initial:initial + 2]
    actual_value = '0'
    if length_hex.startswith('8'):
        length_hex = data[initial + 1 :initial + 4]
        length = int(length_hex, 16)
        value = data[initial + 4 :initial + 4 + length]
        actual_value = data[initial + 4 :]
    else:
        length = int(length_hex, 16)
        if length > 127:
            log_write("!!!!! The length value should be 2 Byte, since it's >127")
        value = data[initial + 2:initial + 2 + length]
        actual_value = data[initial + 2:]
    if length != len(value):
        log_write("!!!!! Length of expected value & actual value is different. Expected = " + str(length), "Actual = " + str(len(value)))
    elif length != len(actual_value) and data.startswith('FFFF01'):
        log_write("!!!!! Length of expected value & actual value is different. Expected = " + str(length), "Actual = " + str(len(actual_value)))
    return length_hex, length, value

def parse_and_get_left_data(data, startwith, value_end, tag_message, error_message, spacing=""):
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
        log_write(spacing + "L => " + ('8' + str(length_hex) if len(str(length_hex)) == 3 else str(length_hex)) + ", " + str(length))
        log_write(spacing + "V => " + str(value))

        value_left = data[value_end + len(length_hex) + length:]  # value after the sequence number
        if len(length_hex) > 2:
            value_left = data[value_end + len(length_hex) + 1 + length:]  # value after the sequence number
    else:
        log_write(tag + " !!!!! " + error_message)
    if tag in ('FFFF01', 'FF45', 'FF49', 'FF46', 'FF4A'):
        value_left = value
        length = len
    return value_left, value

def parse_block(data, desciption, spacing=""):
    result = {}
    i = 0
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
        log_write(f"{spacing} {tag} - {desciption(tag)}")
        log_write(f"{spacing} T => {tag}")
        log_write(f"{spacing} L => {('8' + str(length_hex) if len(str(length_hex)) == 3 else str(length_hex))}, {length_decimal}")
        log_write(f"{spacing} V => {value}")
        log_write(f"{spacing} {data[i:]}")

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
        log_write('!!!!!')
        log_write("                Missed Mandatory Tags In The Header")
        for field in missing_fields:
            i += 1
            log_write("!!!!!"+ str(i) +". " +field)
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
        log_write('!!!!!')
        log_write("                Missed Mandatory Trailer Tags In The Header")
        for field in missing_fields:
            i += 1
            log_write("!!!!!"+ str(i) +". " +field)
    else:
        pass
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
        log_write(f"{spacing} {tag} - {desciption(tag)}")
        log_write(f"{spacing} T => {tag}")
        log_write(f"{spacing} L => {('8' + str(length_hex) if len(str(length_hex)) == 3 else str(length_hex))}, {length_decimal}")
        log_write(f"{spacing} V => {value}")
        log_write(f"{spacing} {data[i:]}")
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
        value_after_sequence_no = parse_and_get_left_data(application_file_header[0], 'DF805D', 6,
                                                          'Sequence Number For Application File Header X M',
                                                          'Unknown Sequence Format for FF49 – File Header Block/ tag DF805D is expected',
                                                          "       ")
        #1.1.1.FF49 – File Header Block
        file_header_block = parse_and_get_left_data(value_after_sequence_no[0], 'FF49', 4, 'FF49 – File Header Block X M',
                                'Unknown File Header Block', "           ")
        parse_file_header_trailer_block(file_header_block[0], 'header', "            ")

def parse_trailer(data):
    if len(data) > 0:
        check_mandatory_fields_for_trailer(data)
        application_file_trailer = parse_and_get_left_data(data, 'FF46', 4,
                                                          'FF46 – Application File Trailer X M',
                                                          'Unknown Application File Trailer',
                                                          " ")
        trailer_value_after_sequence_no = parse_and_get_left_data(application_file_trailer[0], 'DF805D', 6,
                                                          'Sequence Number For Application File Trailer X M',
                                                          'Unknown Sequence Format for FF4A – File Trailer Block/ tag DF805D is expected',
                                                          "       ")
        file_trailer_block = parse_and_get_left_data(trailer_value_after_sequence_no[0], 'FF4A', 4, 'FF4A – File Trailer Block X M',
                                'Unknown File Trailer Block', "           ")
        parse_file_header_trailer_block(file_trailer_block[0], 'trailer', "              ")


def get_description_of_main_block(tag):
    descriptions = {
        'DF8041': 'Application ID 9 M',
        'DF8000': 'Application Type: BTRT01 X O',
        'DF834B': 'Application Status: APRS00= Awaiting processing X O',
        'DF8001': 'Record Number 9 O',
        'DF8002': 'Contract ID X M',
        'DF803A': 'Primary Flag: 1=YES 9 M',
        'DF803D': 'Reject Code: APRJ00=Approved X O',
        'DF803E': 'Application Source X O',
        'DF863C': 'Additional Capture Data X O',
        'DF803F': 'Officer ID X M',
        'DF8040': 'Application Letter Scheme X O',
        'DF8046': 'Delivery Information X O',
        'FF8054': 'ADDITIONAL_PARAMETERS_BLOCK X O  ::: If this is included all DF805D, FF804B, DF8458, DF842C are mandatory',
        'DF8456': 'Reject Reason X O',
        'DF8474': 'Batch ID X O',
        'DF863A': 'Mail Authorisation Status: CMAS0= No restriction X O',
        'DF871A': 'Application External ID X O',
        'DF805D': 'Sequence Number X D',
    }
    return descriptions.get(tag, '!!!!! Unknown')


def get_description_of_customer_block(tag):
    descriptions = {
        'DF8003': 'Customer ID X O',
        'DF8108': 'Customer processing mode 9 O',
        'DF8521': 'Statement scheme 9 O',
        'DF8006': 'VIP Code: CVIP0,CVIP1,CVIP2,CVIP3 9 O',
        'DF8004': 'Customer Description X O',
        'DF8047': 'Delivery Agent Code (Customer Code) X O',
        'DF8379': 'Aggregate Accounts Scheme X O',
        'DF837A': 'Aggregate Scheme 9 O',
        'DF863E': 'Billing Address X O',
        'DF863F': 'Statement Address X O',
        'DF8640': 'Default Card Delivery Address X O',
        'DF8641': 'Default Pin Delivery Address X O',
        'DF8418': 'INN X O',
        'DF8419': 'KPP X O',
        'DF8330': 'OKPO X O',
        'FF8054': 'ADDITIONAL_PARAMETERS_BLOCK X O: Parsed below >>> { ',
        'FF806C': 'DOCUMENT_BLOCK X O: Parsed Below >>> { ',
        'DF805D': 'Sequence Number X D',
    }
    return descriptions.get(tag, '!!!!! Unknown')

def get_description_of_document_block(tag):
    descriptions = {
        'DF8523': 'Document ID 9 O',
        'DF803B': 'Document Type X M',
        'DF803C': 'Number X M',
        'DF8261': 'Series X O',
        'DF8344': 'Authority X O',
        'DF8345': 'Issue Date X O',
        'DF8346': 'Expire Date X O',
        'DF805D': 'Sequence Number X D'
    }
    return descriptions.get(tag, '!!!!! Unknown')
def get_description_of_person_block(tag):
    descriptions = {
        'DF8007': 'Person ID X C',
        'DF8019': 'First Name X C',
        'DF801A': 'Second Name X O',
        'DF801B': 'Surname X C',
        'DF801C': 'Date of Birth X O',
        'DF8108': 'Person processing mode:  X O : 1=Create new, 3=Use existing, 6=Ignore (applicable only if application rejected), 7=Use existing even if it was rejected once, 8=Default processing – no special instructions (equals no , value specified), 9=Update existing (Create if new)',
        'DF800F': 'Company Name X O',
        'DF8013': 'Security ID #1 X O',
        'DF8014': 'Security ID #2 X O',
        'DF8015': 'Security ID #3 X O',
        'DF8016': 'Security ID #4 X O',
        'DF8017': 'Security ID #5 X O',
        'DF8008': 'Sex X O: SEXT1=Male, SEXT2=Female, SEXT3=Transsexual',
        'DF8009': 'Marital Status X O',
        'DF800A': 'Residence X O',
        'DF800B': 'Number of Dependents X O',
        'DF800C': 'Domain X O',
        'DF800D': 'Position X O',
        'DF800E': 'Employed Flag X O',
        'DF8010': 'Annual Income Range X O',
        'DF8011': 'Monthly Deductions X O',
        'DF8018': 'Person’s Style X O',
        'DF8012': 'Language Code X O',
        'DF803B': 'Type of the person’s ID X O',
        'DF803C': 'Number of the person’s ID X O',
        'DF8261': 'Series of the person`s ID X O',
        'DF8344': 'Person`s ID authority X O',
        'DF8345': 'Person`s ID issue date X O',
        'DF8346': 'Person`s ID expire date X O',
        'DF8379': 'Aggregate Accounts Scheme X O',
        'DF837A': 'Aggregate Scheme X O',
        'DF815B': 'GMTOffSet 9 O',
        'DF8431': 'Security Question #1 X O',
        'DF8432': 'Security Question #2 X O',
        'DF8433': 'Security Question #3 X O',
        'DF8434': 'Security Question #4 X O',
        'DF8435': 'Security Question #5 X O',
        'DF8418': 'INN X O',
        'DF827D': 'Insider Flag 9 O',
        'DF8452': 'BKI 9 O',
        'DF8638': 'Country of birth (ISO) X O',
        'DF847С': 'Place of birth X O',
        'DF8639': 'Nationality Code X O',
        'DF863E': 'Billing Address X O',
        'DF863F': 'Statement Address X O',
        'DF8640': 'Default Card Delivery Address X O',
        'DF8641': 'Default Pin Delivery Address X O',
        'DF8682': 'Statement divert flag 9 O',
        'DF8653': 'Statement e-mail flag 9 O',
        'DF8670': 'Risk Profile statuses X O',
        'DF805D': 'Sequence Number X D'
    }
    return descriptions.get(tag, '!!!!! Unknown')

def get_description_of_address_block(tag):
    descriptions = {
        'DF801D': 'Address ID X C',
        'DF801E': 'Address Type X C : ADDR0=Company, ADDR1=Private, ADDR2=Government, ADDR3Delivery Address',
        'DF8108': 'Address processing mode: X O : 1=Create new, 3=Use existing, 6=Ignore (applicable only if application rejected), 7=Use existing even if it was rejected once, 8=Default processing – no special instructions (equals no value specified), 9=Update existing (Create if new)',
        'DF8020': 'Address Line 1 X C',
        'DF8021': 'Address Line 2 X O',
        'DF8022': 'Address Line 3 X O',
        'DF8023': 'Address Line 4 X O',
        'DF8636': 'Address Line 6 X O',
        'DF801F': 'Box Number or House Name X O',
        'DF8478': 'Route X O',
        'DF8024': 'Region X O',
        'DF8025': 'Country (List of Values) X O',
        'DF8026': 'Postal/Zip Code X O',
        'DF8515': 'GPS coords C O',
        'DF8027': 'Primary Phone X O',
        'DF8028': 'Mobile Phone X O',
        'DF8029': 'Secondary Phone X O',
        'DF802A': 'Fax X O',
        'DF802B': 'E-mail X O',
        'DF8530': 'House number X O',
        'DF8532': 'Building number X O',
        'DF8533': 'Building name X O',
        'DF855E': 'REGION TYPE X O',
        'DF855F': 'REGION NAME X O',
        'DF8560': 'DISTRICT NAME X O',
        'DF8561': 'POPULATED AREA TYPE X O',
        'DF8562': 'POPULATED AREA NAME X O',
        'DF8563': 'STREET TYPE X O',
        'DF8564': 'CITY NAME X O',
        'DF8565': 'STREET NAME X O',
        'DF805D': 'Sequence Number X D'
    }
    return descriptions.get(tag, '!!!!! Unknown')

def get_description_of_card_init_block(tag):
    descriptions = {
        'DF802C': 'Card Number X C',
        'DF802F': 'Card Type (List of Values) X M',
        'DF805D': 'Sequence Number X D'

    }
    return descriptions.get(tag, '!!!!! Unknown')

def get_description_of_card_data_block(tag):
    descriptions = {
        'DF8042': 'Embossed Name X M',
        'DF8032': 'Start Date X O',
        'DF8048': 'Express Flag X O',
        'DF8030': 'Default ATM Account X M',
        'DF8031': 'Default POS Account X M',
        'DF802E': 'Card Status X O: CRST0=Valid card, CRST1=Inactive, call issuer, CRST2=Pending card, CRST3=Deleted card',
        'DF8175': 'Hot Card Status X O: CHST0=Valid Card,CHST1=Call Issuer,CHST2=Warm Card,CHST3=Do Not Honor,CHST4=Honor With Id,CHST5=Not Permitted,CHST6=Lost Card, Capture,CHST7=Stolen Card,CHST8=Call Security,CHST9=Invalid Card,CHST10=Pick Up Card, Special Condition,CHST12=Frozen Card,CHST14=Forced Pin Change,CHST15=CREDIT DEBTS,CHST16=VIRTUAL INACTIVE,CHST17=PIN ACTIVATION,CHST18=INSTANT CARD PERSONIFICATION ,WAITING,CHST19=FRAUD PREVENTION',
        'DF802D': 'Card Primary X O: 0 = Not Primary Card, 1 = Primary Card, 2 =Double Card',
        'DF804F': 'Box Number X O: 0=NO, 1=YES',
        'DF8013': 'Security ID #1 X O',
        'DF8431': 'Security Question #1 X O',
        'DF8050': 'Card Re-Link flag X O',
        'DF8219': 'Membership Date D O',
        'DF8222': 'Program Class C O',
        'DF8078': 'Card Expiration Date X O',
        'DF800F': 'Company Name X O',
        'DF820F': 'Cycle Scheme 9 O',
        'DF8210': 'Limits Scheme 9 O',
        'DF8213': 'Fee Scheme 9 O',
        'DF8040': 'Letter Scheme 9 O',
        'DF8454': 'Hot Card Status Reason X O',
        'DF8410': 'Object Service Scheme 9 O',
        'DF840D': 'Cardholder’s Photo Filename X O',
        'DF840E': 'Cardholder’s Sign. Filename X O',
        'DF8520': 'Trouble PIN 9 O',
        'DF8354': 'Card Plast Type X O',
        'DF860B': 'Date of card production 9 O',
        'DF863D': 'Account Class X O',
        'DF8104': 'Card Issue Date D O',
        'DF8077': 'PIN Offset X O',
        'DF8204': 'Plastic Status X O',
        'DF8033': 'Prepaid card account from num D O',
        'DF8710': 'Prepaid card selling way 9 O',
        'DF805D': 'Sequence Number X D'

    }
    return descriptions.get(tag, '!!!!! Unknown')

def get_description_of_account_init_block(tag):
    descriptions = {
        'DF8033': 'Account number X M',
        'DF8035': 'Account Type X M: ACCTANY=Any account type,ACCTC01 – ACCTC99=Credit1st – Credit 99th,ACCTD01 – ACCTD99=Checking 1st – Checking 99th,ACCTL01 – ACCTL08=Loan 1st – Loan 8th,ACCTO01 – ACCTO99=Others 1st – Others 99th,ACCTS01 – ACCTS99=Savings 1st – Savings 99t',
        'DF8034': 'Currency Code (List of Values) X M',
        'DF805D': 'Sequence Number X D'
    }
    return descriptions.get(tag, '!!!!! Unknown')

def get_description_of_account_data_block(tag):
    descriptions = {
        'DF8032': 'Start Date X O',
        'DF8036': 'Account Status: ACST1=Active,ACST2=Frozen,ACST3=Closed,ACST4=Suspend,ACST5=ATM transactions only,ACST6=POS transactions only,ACST7=Deposits only,ACST8=In collections,ACST9=Deleted,X O',
        'DF8037': 'Source for opening the account X O',
        'DF8038': 'Destination for closing the account X O',
        'DF8040': 'Letter Scheme 9 O',
        'DF804C': 'Account donor flag: 0=NO,1=YES,X O',
        'DF804D': 'Account recipient flag: 0=NO,1=YES,X O',
        'DF8051': 'Account Link to Bank Card flag: 0=NO,1=YES,X O',
        'DF820F': 'Cycle Scheme 9 O',
        'DF8210': 'Limits Scheme 9 O',
        'DF8213': 'Fee Scheme 9 O',
        'DF8214': 'Rates Scheme 9 O',
        'DF834F': 'Project Code X O',
        'DF8350': 'Bank Account Number X O',
        'DF8358': 'Project Description X O',
        'DF8379': 'Aggregate Accounts Scheme X O',
        'DF837A': 'Aggregate Entries Scheme X O',
        'DF8400': 'Priority 9 O',
        'DF845E': 'Account maximum available balance 9 O',
        'DF820E': 'Status Reason X O',
        'DF805D': 'Sequence Number X D'
    }
    return descriptions.get(tag, '!!!!! Unknown')

def get_description_of_additional_parameters_block(tag):
    descriptions = {
        'FF804B': 'PARAMETER_BLOCK X M',
        'DF805D': 'Sequence Number X D'
    }
    return descriptions.get(tag, '!!!!! Unknown')
def get_description_of_reference_block(tag):
    descriptions = {
        'DF8061': 'Reference Tag – Link Account with Card X M',
        'DF8063': 'Reference Tag –Card vs Additional Service X O',
        'DF8138': 'Reference Tag –Unlink Account from Card X O',
        'DF8162': 'Reference Tag – Account vs Additional Service X O',
        'DF805D': 'Sequence Number X D'
    }
    return descriptions.get(tag, '!!!!! Unknown')
def check_mandatory_fields_for_btrt01(data):
    mandatory_fields = {
        'FFFF01':'Cardholder Application BTRT01',
        'FF2E': 'MAIN_BLOCK',
        'FF2C': 'CARDHOLDER_BLOCK',
        'FF24': 'CARD_BLOCK',
        'FF26': 'ACCOUNT_BLOCK',
        'FF3C': 'REFERENCE_BLOCK',
        'DF8000': 'Application Type: BTRT01',
        'DF8002': 'Contract ID',
        'DF803F': 'Officer ID',
        'FF22': 'PERSON_BLOCK',
        'FF2A': 'ADDRESS_BLOCK',
        'FF33': 'CARD_INIT_BLOCK',
        'FF34': 'CARD_DATA_BLOCK',
        'DF802F': 'Card Type (List of Values)',
        'DF8042': 'Embossed Name',
        # 'DF8030': 'Default ATM Account',
        # 'DF8031': 'Default POS Account',
        'FF36': 'ACCOUNT_INIT_BLOCK',
        'DF8033': 'Account number',
        'DF8035': 'Account Type',
        'DF8034': 'Currency Code (List of Values)',
        'DF8061': 'Reference Tag – Link Account with Card'
    }
    missing_fields = []
    for key, value in mandatory_fields.items():
        if key not in data:
            missing_fields.append(f"'{key}': '{value}")

    if missing_fields:
        i = 0
        log_write('!!!!!')
        log_write("                Missed Mandatory Tags In The Header")
        for field in missing_fields:
            i += 1
            log_write("!!!!! "+ str(i) +". " +field)
    else:
        pass

def parse_cardholder_application_btrt01(data):
    if len(data) > 0:
        # 3.1. FFFF01 – Cardholder Application BTRT01
        check_mandatory_fields_for_btrt01(data)
        cardholder_application = parse_and_get_left_data(data, 'FFFF01', 6,
                                                         'FFFF01 – Cardholder Application BTRT01 X M',
                                                         'Unknown Cardholder Application BTRT01',
                                                         " ")
        value_after_sequence_no = parse_and_get_left_data(cardholder_application[0], 'DF805D', 6,
                                                          'Sequence Number For Cardholder Application BTRT01 X M',
                                                          'Unknown Sequence Format for Cardholder Application BTRT01/ tag DF805D is expected',
                                                          "       ")
        # 3.1.1.FF2E – MAIN_BLOCK
        FF2E_main_block = parse_and_get_left_data(value_after_sequence_no[0], 'FF2E', 4, 'FF2E – MAIN_BLOCK X M',
                                                  'Unknown – MAIN_BLOCK', "           ")

        value_after_sequence_main_block = parse_and_get_left_data(FF2E_main_block[1], 'DF805D', 6,
                                                                  'Sequence Number For Main Block X M',
                                                                  'Unknown Sequence Format for Main Block/ tag DF805D is expected',
                                                                  "             ")
        parse_block(value_after_sequence_main_block[0], get_description_of_main_block, "               ")
        # 3.1.2 FF20 – CUSTOMER_BLOCK
        FF20_customer_block = parse_and_get_left_data(FF2E_main_block[0], 'FF20', 4, 'FF20 – CUSTOMER_BLOCK X M',
                                                      'Unknown – CUSTOMER_BLOCK', "           ")

        value_after_sequence_customer_block = parse_and_get_left_data(FF20_customer_block[1], 'DF805D', 6,
                                                                      'Sequence Number For Customer Block X M',
                                                                      'Unknown Sequence Format for Customer Block/ tag DF805D is expected',
                                                                      "             ")
        parse_block(value_after_sequence_customer_block[0], get_description_of_customer_block, "               ")

        # 3.1.2.1 FF8054 – ADDITIONAL_PARAMETERS_BLOCK
        if 'FF8054' in value_after_sequence_customer_block[0]:
            FF8054_additional_parameters_block = value_after_sequence_customer_block[0][
                                    value_after_sequence_customer_block[0].index('FF8054'):]
            FF8054_additional_parameters_parsed = parse_and_get_left_data(FF8054_additional_parameters_block, 'FF8054', 6,
                                                                   'FF8054 – ADDITIONAL_PARAMETERS_BLOCK X M',
                                                                   'Unknown – ADDITIONAL_PARAMETERS_BLOCK',
                                                                   "                 ")
            value_after_sequence_no_document_block_block = parse_and_get_left_data(FF8054_additional_parameters_parsed[1],
                                                                                   'DF805D', 6,
                                                                                   'Sequence Number For Additional Parameters Block X M',
                                                                                   'Unknown Sequence Format for Additional Parameters Block/ tag DF805D is expected',
                                                                                   "                    ")
            parse_block(value_after_sequence_no_document_block_block[0],
                        get_description_of_additional_parameters_block, "                    ")

        # 3.1.2.2 FF806C – DOCUMENT_BLOCK
        if 'FF806C' in value_after_sequence_customer_block[0]:
            FF806C_document_block = value_after_sequence_customer_block[0][value_after_sequence_customer_block[0].index('FF806C'):]
            FF806C_document_block_parsed = parse_and_get_left_data(FF806C_document_block, 'FF806C', 6,
                                                                     'FF806C – DOCUMENT_BLOCK X O',
                                                                     'Unknown – DOCUMENT_BLOCK',
                                                                     "                 ")
            value_after_sequence_no_document_block_block = parse_and_get_left_data(FF806C_document_block_parsed[1],
                                                                                     'DF805D', 6,
                                                                                     'Sequence Number For Document Block X M',
                                                                                     'Unknown Sequence Format for Document Block/ tag DF805D is expected',
                                                                                     "                    ")
            parse_block(value_after_sequence_no_document_block_block[0],
                        get_description_of_document_block, "                    ")

        # 3.1.3.FF2C – CARDHOLDER_BLOCK
        FF2C_cardholder_block = parse_and_get_left_data(FF20_customer_block[0], 'FF2C', 4,
                                                        'FF2C – CARDHOLDER_BLOCK X M',
                                                        'Unknown – CARDHOLDER_BLOCK', "           ")
        value_after_sequence_no_for_cardholder = parse_and_get_left_data(FF2C_cardholder_block[1], 'DF805D', 6,
                                                                         'Sequence Number For Cardholder Block X M',
                                                                         'Unknown Sequence Format for Cardholder Block/ tag DF805D is expected',
                                                                         "              ")
        FF22_person_block = parse_and_get_left_data(value_after_sequence_no_for_cardholder[0], 'FF22', 4,
                                                    'FF22 – PERSON_BLOCK X M',
                                                    'Unknown – PERSON_BLOCK', "                 ")
        value_after_sequence_no_for_person_block = parse_and_get_left_data(FF22_person_block[1], 'DF805D', 6,
                                                                           'Sequence Number For Person Block X M',
                                                                           'Unknown Sequence Format for Person Block/ tag DF805D is expected',
                                                                           "                   ")

        parse_block(value_after_sequence_no_for_person_block[0], get_description_of_person_block, "                   ")
        # 3.1.3.2 – FF2A – ADDRESS_BLOCK
        FF2A_address_block = parse_and_get_left_data(FF22_person_block[0], 'FF2A', 4,
                                                     'FF2A – ADDRESS_BLOCK X M',
                                                     'Unknown – ADDRESS_BLOCK', "                 ")
        value_after_sequence_no_for_address_block = parse_and_get_left_data(FF2A_address_block[1], 'DF805D', 6,
                                                                            'Sequence Number For Address Block X M',
                                                                            'Unknown Sequence Format for Address Block/ tag DF805D is expected',
                                                                            "                  ")
        parse_block(value_after_sequence_no_for_address_block[0], get_description_of_address_block,
                    "                  ")

        # 3.1.4.FF24 – CARD_BLOCK
        FF24_card_block = parse_and_get_left_data(FF2C_cardholder_block[0], 'FF24', 4,
                                                  'FF24 – CARD_BLOCK X M',
                                                  'Unknown – CARD_BLOCK', "           ")
        value_after_sequence_no_for_card = parse_and_get_left_data(FF24_card_block[1], 'DF805D', 6,
                                                                   'Sequence Number For Card Block X M',
                                                                   'Unknown Sequence Format for Card Block/ tag DF805D is expected',
                                                                   "              ")
        # 3.1.4.1 FF33 – CARD_INIT_BLOCK
        FF33_card_init_block = parse_and_get_left_data(value_after_sequence_no_for_card[0], 'FF33', 4,
                                                       'FF33 – CARD_INIT_BLOCK X M',
                                                       'Unknown – CARD_INIT_BLOCK', "                 ")
        value_after_sequence_no_for_card_init_block = parse_and_get_left_data(FF33_card_init_block[1], 'DF805D', 6,
                                                                              'Sequence Number For Card Init Block X M',
                                                                              'Unknown Sequence Format for Card Init Block/ tag DF805D is expected',
                                                                              "                    ")
        parse_block(value_after_sequence_no_for_card_init_block[0], get_description_of_card_init_block,
                    "                    ")

        # 3.1.4.2 FF34 – CARD_DATA_BLOCK
        FF34_card_data_block = parse_and_get_left_data(FF33_card_init_block[0], 'FF34', 4,
                                                       'FF34 – CARD_DATA_BLOCK X M',
                                                       'Unknown – CARD_DATA_BLOCK', "                 ")
        value_after_sequence_no_for_card_data_block = parse_and_get_left_data(FF34_card_data_block[1], 'DF805D', 6,
                                                                              'Sequence Number For Card Data Block X M',
                                                                              'Unknown Sequence Format for Card Data Block/ tag DF805D is expected',
                                                                              "                    ")
        parse_block(value_after_sequence_no_for_card_data_block[0],
                    get_description_of_card_data_block, "                    ")

        FF24_card_block_all = FF2C_cardholder_block[0]  # Card Block Uncommon Tags
        # 3.1.4.3 FF30 – REG_RECORD_BLOCK
        if 'FF30' in FF24_card_block_all:
            FF30_reg_record_block = FF24_card_block_all[FF24_card_block_all.index('FF30'):]
            parse_and_get_left_data(FF30_reg_record_block, 'FF30', 4,
                                    'FF30 – REG_RECORD_BLOCK X O',
                                    'Unknown – REG_RECORD_BLOCK', "                 ")
        # 3.1.4.4 FF8026 – FLEXIBLE_LIMIT_BLOCK
        if 'FF8026' in FF24_card_block_all:
            FF8026_flexible_limit_block = FF24_card_block_all[FF24_card_block_all.index('FF8026'):]
            parse_and_get_left_data(FF8026_flexible_limit_block, 'FF8026', 6,
                                    'FF8026 – FLEXIBLE_LIMIT_BLOCK X O',
                                    'Unknown – FLEXIBLE_LIMIT_BLOCK', "                 ")
        # 3.1.4.5 FF805E – DELIVERY_BLOCK
        if 'FF805E' in FF24_card_block_all:
            FF805E_delivery_block = FF24_card_block_all[FF24_card_block_all.index('FF805E'):]
            parse_and_get_left_data(FF805E_delivery_block, 'FF805E', 6,
                                    'FF805E – DELIVERY_BLOCK X O',
                                    'Unknown – DELIVERY_BLOCK', "                 ")
        # 3.1.4.6 FF8054 – ADDITIONAL_PARAMETERS_BLOCK
        if 'FF8054' in FF24_card_block_all:
            FF8054_additional_parameters_block = FF24_card_block_all[FF24_card_block_all.index('FF8054'):]
            parse_and_get_left_data(FF8054_additional_parameters_block, 'FF8054', 6,
                                    'FF8054 – REG_RECORD_BLOCK X O',
                                    'Unknown – REG_RECORD_BLOCK', "                 ")
        # 3.1.5 FF26 – ACCOUNT_BLOCK
        FF26_account_block = FF24_card_block[0]
        FF26_account_block_parsed = parse_and_get_left_data(FF26_account_block, 'FF26', 4,
                                                            'FF26 – ACCOUNT_BLOCK X M',
                                                            'Unknown – ACCOUNT_BLOCK', "           ")
        value_after_sequence_no_for_account_block = parse_and_get_left_data(FF26_account_block_parsed[1], 'DF805D', 6,
                                                                            'Sequence Number For Account Block X M',
                                                                            'Unknown Sequence Format for Account Block/ tag DF805D is expected',
                                                                            "              ")
        # 3.1.5.1 FF36 – ACCOUNT_INIT_BLOCK
        FF36_account_init_block = parse_and_get_left_data(value_after_sequence_no_for_account_block[0], 'FF36', 4,
                                                          'FF36 – ACCOUNT_INIT_BLOCK X M',
                                                          'Unknown – ACCOUNT_INIT_BLOCK', "                 ")
        value_after_sequence_no_for_account_init_block = parse_and_get_left_data(FF36_account_init_block[1], 'DF805D',
                                                                                 6,
                                                                                 'Sequence Number For Account Init Block X M',
                                                                                 'Unknown Sequence Format for Account Init Block/ tag DF805D is expected',
                                                                                 "                    ")
        parse_block(value_after_sequence_no_for_account_init_block[0], get_description_of_account_init_block,
                    "                    ")

        # 3.1.5.2 FF37 – ACCOUNT_DATA_BLOCK
        if 'FF37' in FF26_account_block:
            FF37_account_data_block = FF26_account_block[FF26_account_block.index('FF37'):]
            FF37_account_data_block_parsed = parse_and_get_left_data(FF37_account_data_block, 'FF37', 4,
                                                                     'FF37 – ACCOUNT_DATA_BLOCK X O',
                                                                     'Unknown – ACCOUNT_DATA_BLOCK',
                                                                     "                 ")
            value_after_sequence_no_for_account_data_block = parse_and_get_left_data(FF37_account_data_block_parsed[1],
                                                                                     'DF805D', 6,
                                                                                     'Sequence Number For Account Data Block X M',
                                                                                     'Unknown Sequence Format for Account Data Block/ tag DF805D is expected',
                                                                                     "                    ")
            parse_block(value_after_sequence_no_for_account_data_block[0],
                        get_description_of_account_data_block, "                    ")

            # 3.1.5.3 FF8026 – FLEXIBLE_LIMIT_BLOCK
            if 'FF8026' in FF26_account_block:
                FF8026_flexible_block = FF26_account_block[FF26_account_block.index('FF8026'):]
                FF8026_flexible_limit_parsed = parse_and_get_left_data(FF8026_flexible_block, 'FF8026', 6,
                                                                       'FF8026 – FLEXIBLE_LIMIT_BLOCK X O',
                                                                       'Unknown – FLEXIBLE_LIMIT_BLOCK',
                                                                       "                 ")
            # 3.1.5.4 FF8054 – ADDITIONAL_PARAMETERS_BLOCK
            if 'FF8054' in FF26_account_block:
                FF8054_additional_parameters_block = FF26_account_block[FF26_account_block.index('FF8054'):]
                FF8054_flexible_limit_parsed = parse_and_get_left_data(FF8054_additional_parameters_block, 'FF8054', 6,
                                                                       'FF8054 – ADDITIONAL_PARAMETERS_BLOCK X O',
                                                                       'Unknown – ADDITIONAL_PARAMETERS_BLOCK',
                                                                       "                 ")
            # 3.1.6 FF2F – ADDITIONAL_SERVICE_BLOCK
            if 'FF2F' in FF26_account_block:
                FF2F_additional_service_block = FF26_account_block[FF26_account_block.index('FF2F'):]
                FF2F_additional_service_block_parsed = parse_and_get_left_data(FF2F_additional_service_block, '', 4,
                                                                               'FF2F – ADDITIONAL_SERVICE_BLOCK X O',
                                                                               'Unknown – ADDITIONAL_SERVICE_BLOCK',
                                                                               "                 ")
                value_after_sequence_no_for_additional_service_block = parse_and_get_left_data(
                    FF2F_additional_service_block_parsed[1], 'DF805D', 6,
                    'Sequence Number For Additional Service Block X M',
                    'Unknown Sequence Format for Additional Service Block/ tag DF805D is expected',
                    "              ")

            # 3.1.7 FF3C – REFERENCE_BLOCK
            FF3C_reference_block = parse_and_get_left_data(FF26_account_block_parsed[0], 'FF3C', 4,
                                                           'FF3C – REFERENCE_BLOCK X M',
                                                           'Unknown – REFERENCE_BLOCK', "           ")

            value_after_sequence_reference_block = parse_and_get_left_data(FF3C_reference_block[1], 'DF805D', 6,
                                                                           'Sequence Number For Reference Block X M',
                                                                           'Unknown Sequence Format for Reference Block/ tag DF805D is expected',
                                                                           "             ")
            parse_block(value_after_sequence_reference_block[0], get_description_of_reference_block, "               ")

# Initialize the last_found_position variable and search count
last_found_positions = []  # Use a list to store all found positions
current_position_index = 0  # Index to track the current position

# Function to find the next occurrence in the list
# def find_next_occurrence():
#     global current_position_index
#     if last_found_positions:
#         current_position_index = (current_position_index + 1) % len(last_found_positions)
#         text_widget.mark_set(tk.INSERT, last_found_positions[current_position_index])
#         text_widget.see(last_found_positions[current_position_index])
def contact_developer():
    # Replace 'https://example.com' with your desired link
    webbrowser.open('https://www.linkedin.com/in/bruk-hailu-521065190/')
# Function to highlight all lines containing "!!!!" in red
def highlight_errors():
    text_widget.tag_configure("error", background="red")
    text_widget.mark_set("error_start", "1.0")
    while True:
        start = text_widget.search("!!!!", "error_start", stopindex=tk.END)
        if not start:
            break
        end = text_widget.index(f"{start} lineend")
        text_widget.tag_add("error", start, end)
        text_widget.mark_set("error_start", f"{end}+1c")

def find_all_text(event=None):
    global last_found_positions, current_position_index  # Use the global variables
    search_text = simpledialog.askstring("Find All", "Enter text to find:")
    if search_text:
        # Start searching from the beginning in both raw and processed text
        raw_start_pos = "1.0"
        raw_occurrences = 0
        last_found_positions = []  # Clear the list of found positions
        current_position_index = 0  # Reset the current position index

        # Search in raw text
        while True:
            raw_start_pos = text_widget.search(search_text, raw_start_pos, tk.END)
            if not raw_start_pos:
                break
            raw_end_pos = f"{raw_start_pos}+{len(search_text)}c"
            text_widget.tag_add(tk.SEL, raw_start_pos, raw_end_pos)
            last_found_positions.append(raw_start_pos)
            raw_start_pos = raw_end_pos
            raw_occurrences += 1

        # Search in processed text
        processed_text = text_widget.get("1.0", tk.END)
        processed_start_pos = 0
        processed_occurrences = 0

        while True:
            processed_start_pos = processed_text.find(search_text, processed_start_pos)
            if processed_start_pos != -1:
                processed_end_pos = processed_start_pos + len(search_text)
                text_widget.tag_add(tk.SEL, f"{processed_start_pos + 1}.0", f"{processed_end_pos + 1}.0")
                last_found_positions.append(f"{processed_start_pos + 1}.0")
                processed_start_pos = processed_end_pos
                processed_occurrences += 1
            else:
                break

        # Configure the highlight color
        text_widget.tag_config(tk.SEL, background="red")

        # Display the total count of occurrences
        total_occurrences = processed_occurrences
        if total_occurrences == 0:
            messagebox.showinfo("Find All", f"No occurrences found for '{search_text}'.")
        else:
            messagebox.showinfo("Find All", f"Found {total_occurrences} occurrences of '{search_text}'.")

# Function to open a file dialog and load the selected text file
def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.*"), ("All Files", "*.*")])
    if file_path:
        with open(file_path, 'r') as file:
            text = file.read()
        text_widget.delete(1.0, tk.END)  # Clear the existing text
        text_widget.insert(tk.END, text)  # Insert the content of the file
        input_path_entry.delete(0, tk.END)
        input_path_entry.insert(0, file_path)

# Function to process the file
def process_file():
    clear_log_file()
    input_file_path = input_path_entry.get()
    if not input_file_path:
        messagebox.showerror("Error", "Please select an input file.")
        return
    output_file_path = "Parsed_Result"

    try:
        with open(input_file_path, 'r') as input_file:
            lines = input_file.readlines()
            i = 0
            for line in lines:
                i += 1
                log_write("======================================= Line " + str(
                    i) + " =======================================")
                if i == 1:
                    log_write(
                        'File Header Start ------------------------------------------------------------------------')
                    parse_header(line.strip())
                    log_write(
                        'File Header End ----------------------------------------------------------------------------\n')
                elif i == len(lines):
                    log_write(
                        'File Trailer Start -------------------------------------------------------------------------')
                    parse_trailer(line.strip())
                    log_write(
                        'File Trailer End -------------------------------------------------------------------------\n')
                else:
                    try:
                        parse_cardholder_application_btrt01(line.strip())
                        log_write("======================================= Line " + str(
                            i) + " End ===================================\n")
                    except:
                        log_write("!!!!! Error occur in line " + str(i))

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return

    # Close the redirected output file
    sys.stdout.close()
    # Reset sys.stdout to the original value (usually the console)
    sys.stdout = sys.__stdout__

    # Read the content of the Processed_Result file
    try:
        with open(output_file_path, 'r') as result_file:
            result_content = result_file.read()
            if "!!!" in result_content:
                messagebox.showerror("Error", "File contains some errors. Please find & check the lines contains !!!!!")
            else:
                messagebox.showinfo("Success", "Parsed with success.")
        # Update the text_widget with the processed content
        text_widget.delete(1.0, tk.END)  # Clear the existing text
        text_widget.insert(tk.END, result_content)  # Insert the processed content
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while reading the result file: {str(e)}")

    # Open the folder containing the result file with the default file explorer
    result_folder = os.path.dirname(os.path.abspath(output_file_path))
    try:
        if sys.platform.startswith('win'):
            subprocess.Popen(['explorer', result_folder])  # Windows
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', result_folder])  # macOS
        else:
            subprocess.Popen(['xdg-open', result_folder])  # Linux
    except Exception as e:
        print(f"An error occurred while opening the folder: {str(e)}")


root = tk.Tk()
root.title("CBS Card File Integration (IIA) Parser")
root.resizable(0, 0)

# Set a uniform padding for all widgets
uniform_pad = 5

# Create a label and entry for the input file path
input_path_label = ttk.Label(root, text="Input File:")
input_path_label.grid(row=0, column=0, padx=10, pady=uniform_pad, sticky="e")

input_path_entry = ttk.Entry(root, width=40)
input_path_entry.grid(row=0, column=1, padx=10, pady=uniform_pad, sticky="ew")

# Create a button to browse for the input file
browse_button = ttk.Button(root, text="Browse", command=open_file)
browse_button.grid(row=0, column=2, padx=10, pady=uniform_pad, sticky="w")

# Create a "Process" button to process the file
process_button = ttk.Button(root, text="Process", command=process_file)
process_button.grid(row=0, column=3, padx=10, pady=uniform_pad, sticky="w")

# Create a "contact developer"
contact_developer = ttk.Button(root, text="<-About->", command=contact_developer)
contact_developer.grid(row=0, column=4, padx=10, pady=uniform_pad, sticky="e")

# Create a ScrolledText widget for displaying the text with vertical and horizontal scrollbars
text_widget = scrolledtext.ScrolledText(root, wrap=tk.NONE)
text_widget.grid(row=1, column=0, columnspan=5, padx=10, pady=uniform_pad, sticky="nsew")

# Create vertical scrollbar and attach it to the text widget
scrollbar_y = tk.Scrollbar(root, command=text_widget.yview)
scrollbar_y.grid(row=1, column=5, sticky="ns")
text_widget.config(yscrollcommand=scrollbar_y.set)

# Create horizontal scrollbar and attach it to the text widget
scrollbar_x = tk.Scrollbar(root, command=text_widget.xview, orient=tk.HORIZONTAL)
scrollbar_x.grid(row=2, column=0, columnspan=5, sticky="ew")
text_widget.config(xscrollcommand=scrollbar_x.set)

# Use a fixed-width font for better alignment
text_widget.configure(font=("Courier", 12))

# Create a menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# Create a "Text" menu
text_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Find", menu=text_menu)

# Add "Find" option to the "Text" menu and bind Ctrl + F
text_menu.add_command(label="Find All", command=find_all_text)
root.bind("<Control-f>", find_all_text)

# Highlight lines containing "!!!!" in red
highlight_errors()

# Create a label for displaying the search message at the last bottom
search_label = ttk.Label(root, text="Note: L => Hex, Dec & Find !!!!! for error (Ctrl + F)")
search_label.grid(row=3, column=0, columnspan=5, padx=10, pady=uniform_pad, sticky="w")

# Run the GUI
root.mainloop()