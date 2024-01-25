# 3. Interface File Format Record Layout Definition
# Cardholder Application BTRT01
# 3.1. FFFF01 – Cardholder Application BTRT01
import sys
import logging
from datetime import datetime
#
#
# now = datetime.now()
# date_log = now.strftime("%d%m%Y")
# # Configure logging to write to a log file
# logging.basicConfig(filename=f'{date_log}.log', level=logging.INFO, format='%(asctime)s - %(message)s')
#
# def log_write(*args, **kwargs):
#     log_entry = ' '.join(map(str, args))
#     # log_entry_with_datetime = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {log_entry}"
#     logging.info(log_entry)
#
# # Redirect sys.stdout to the log file
# sys.stdout = open(date_log + '.log', 'a')
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
        # if length != len(value):
        #     print("!!!!! Length of expected value & actual value is different. Expected = " + str(length), "Actual = " + str(len(value)))
    else:
        length = int(length_hex, 16)
        if length > 127:
            print("!!!!! The length value should be 2 Byte, since it's >127")
        value = data[initial + 2:initial + 2 + length]
        actual_value = data[initial + 2:]
    if length != len(value):
        print("!!!!! Length of expected value & actual value is different. Expected = " + str(length), "Actual = " + str(len(value)))
    elif length != len(actual_value) and data.startswith('FFFF01'):
        print("!!!!! Length of expected value & actual value is different. Expected = " + str(length), "Actual = " + str(len(actual_value)))
    return length_hex, length, value

def parse_and_get_left_data(data, startwith, value_end, tag_message, error_message, spacing=""):
    tag = data[0:value_end]
    value_left = ''
    value = ''
    print(spacing + data)
    if data.startswith(startwith):
        value_length = get_length_value(data, value_end)
        length_hex = value_length[0]
        length = value_length[1]
        value = value_length[2]
        print(spacing + tag_message)
        print(spacing + "T => " + tag)
        print(spacing + "L => " + str(length_hex) + ", " + str(length))
        print(spacing + "V => " + str(value))

        value_left = data[value_end + len(length_hex) + length:]  # value after the sequence number
        if len(length_hex) > 2:
            value_left = data[value_end + len(length_hex) + 1 + length:]  # value after the sequence number
    else:
        print(tag + " => " + error_message)
    if tag in ('FFFF01', 'FF45', 'FF49', 'FF46', 'FF4A'):
        value_left = value
        length = len
    return value_left, value

def parse_block(data, desciption, spacing=""):
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
                print(" !!!!! The length value should be 2 Byte, since it's >127")
        length_decimal = int(length_hex, 16)

        value = data[i:i + length_decimal]
        i += length_decimal

        result[tag] = {
            'Tag': tag,
            'Length (Hex)': length_hex,
            'Length (Decimal)': length_decimal,
            'Value': value
        }
        # Format the output
        print(f"{spacing} {data[i:]}")
        print(f"{spacing} {tag} - {desciption(tag)}")
        print(f"{spacing} T => {tag}")
        print(f"{spacing} L => {length_hex}, {length_decimal}")
        print(f"{spacing} V => {value}")
    print(formatted_output)
    return formatted_output

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
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print("                Missed Mandatory Tags In The Header")
        for field in missing_fields:
            i += 1
            print("!!!!!!!!!! "+ str(i) +". " +field)
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
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print("                Missed Mandatory Trailer Tags In The Header")
        for field in missing_fields:
            i += 1
            print("!!!!!!!!!! "+ str(i) +". " +field)
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
                print(" !!!!! The length value should be 2 Byte, since it's >127")
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
        print(f"{spacing} {data[i:]}")
        print(f"{spacing} {tag} - {desciption(tag)}")
        print(f"{spacing} T => {tag}")
        print(f"{spacing} L => {length_hex}, {length_decimal}")
        print(f"{spacing} V => {value}")
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
        'FF8054': 'ADDITIONAL_PARAMETERS_BLOCK X O: Please refer 3.1.2.1.1 FF804B – PARAMETER_BLOCK',
        'FF806C': 'DOCUMENT_BLOCK X O: Please refer 3.1.2.2 FF806C – DOCUMENT_BLOCK',
        'DF805D': 'Sequence Number X D',
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
        'DF8030': 'Default ATM Account',
        'DF8031': 'Default POS Account',
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
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        print("                Missed Mandatory Tags In The Header")
        for field in missing_fields:
            i += 1
            print("!!!!! "+ str(i) +". " +field)
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

# data = "FFFF018333DF805D011FF2E4FDF805D012DF800006BTRT01DF80010212DF80020231DF803A011DF803F05ADMINDF803D06APRJ00FF2072DF805D013DF80030840835100DF800605CVIP0DF8108011DF80040DFAYISA RIGITAFF806C26DF805D014DF803B05IDTP1DF803C0840835100FF2C80FBDF805D015FF228082DF805D016DF80070840835100DF801906FAYISADF801A06RIGITADF801B05AGAMADF8108011DF800805SEXT1DF800A05RSDN1DF803B05IDTP1DF803C0840835100FF2A62DF805D017DF801E05ADDR1DF8108011DF802004BUSADF802104BUSADF802204DAWODF802503231DF80290C251925400026FF2480BDDF805D018FF3313DF805D019DF802F0232FF348093DF805D0210DF80420DFAYISA RIGITADF802D011DF804806EXPF00DF80300D1040835100101DF80310D1040835100101DF802E05CRST0DF817505CHST0DF804F011DF80320809162023FF266FDF805D0211FF3639DF805D0212DF80330D1040835100101DF803507ACCTS01DF803403230FF3720DF805D0213DF803605ACST1DF8051011FF3C1ADF805D0214DF80610800080011"
# parse_cardholder_application_btrt01(data)

with open('SIB_BTRT01_08312023_5_54_2023.txt') as f:
    lines = f.readlines()
# Check if the file is empty
if not lines:
    print("The file is empty.")
else:
    i = 0
    for line in lines:
        i += 1
        print("======================================= Line " + str(i) + " =======================================")
        if i == 1:
            print('File Header Start ------------------------------------------------------------------------')
            parse_header(line.strip())
            print('File Header End ----------------------------------------------------------------------------\n')
        elif i == len(lines):
            print('File Trailer Start -------------------------------------------------------------------------')
            parse_trailer(line.strip())
            print('File Trailer End -------------------------------------------------------------------------\n')
        else:
            try:
                parse_cardholder_application_btrt01(line.strip())
                print("======================================= Line " + str(
                    i) + " End ===================================\n")
            except:
                print("!!!!! Error occur in line " + str(i))


# Close the redirected output file
sys.stdout.close()
# Reset sys.stdout to the original value (usually the console)
sys.stdout = sys.__stdout__