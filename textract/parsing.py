
import json
import trp
import boto3
import re
import os
from datetime import datetime, timedelta

# path=('/Users/.../Feb-19-2024_110217.json') ##Prateek Agarwal

def parse_data(path):
    with open(path) as f:
        response = f.read()
        results = json.loads(response)
        doc = trp.Document(results)
        
    split_sec=response.split(",")
    
    def findWholeWord(w):
        return re.compile(re.escape(r'\b{0})\b'.format(w)), flags=re.IGNORECASE).search
            
    for page in doc.pages:
        for field in page.form.fields:
            if hasattr(field.key, 'text') and hasattr(field.value, 'text'):
                #print("field.key:{}, Value:{}".format(field.key.text, field.value.text))
                a=format(field.key.text)
                b=format(field.value.text)
                if findWholeWord('A/C')(a) or findWholeWord('AC')(a) :
                    a="account"
                if findWholeWord('ifs')(a) :
                    a="IFS"
                if findWholeWord('\u20b9')(a) or findWholeWord('₹')(a) or findWholeWord('rupees')(a) or (('₹') in a):
                    a="amount"
                if findWholeWord('Y Y Y Y')(a) or findWholeWord('M M Y Y Y Y')(a) :
                    a="date"
                if findWholeWord('VALID FOR')(a):
                    if len(str(re.findall(r'\d{8}', b)))==12:
                        a="date"
                globals()[f'{a}']=str(b)
                
                
    micr_string = re.search(r'"Text": "⑈[0-9]+⑈\s+[0-9]+⑆\s+[0-9]+⑈\s+[0-9]+.*"', response)
    bank_string = re.findall(r'"Text": ".*Bank.*"', response)
    
    for item in split_sec:
        
        item_check=re.search(r'"Text": ".*[0-9]+.*\s+[0-9]+.*\s+[0-9]+.*\s+[0-9]+.*"', item)
        if item_check:
            micr=(re.findall(r'\d{9}', item_check[0]))[-1]
            print("MICR String:", micr)
            break
        else:
            micr="NA"
            
    def micr_check(micr):
        if micr.isnumeric():
            lnth=len(micr)
            if lnth==9:
                micr_status="valid"
                micr_pincode=micr[:3]
                micr_bankcode=micr[3:6]
                micr_branchcode=micr[-3:]
            else:
                micr_status="invalid"
        else:
            micr_status="invalid"
        return [micr_status, micr_pincode, micr_bankcode, micr_branchcode]
    
    micr_check(micr)
    date_formatted=datetime.strptime(date, '%d%m%Y') # noqa
    d_diff = (datetime.today() - date_formatted).days
    
    
    def date_check(date):
        date_formatted=datetime.strptime(date, '%d%m%Y')
        d_diff = (datetime.today() - date_formatted).days
        if d_diff <90:
            date_status="valid"
        else:
            date_status="invalid"
        return date_status
    
    def confidence_check(word):
        lines=[]
        for i, line in enumerate(response.split(', "')):
            lines.append(line)
            if line.find(word) != -1:
                lin=(lines[max(i - 1, 0) : i + 1])[0]
                temp = re.findall(r'\d+', lin)
                res = list(map(int, temp))
                return res[0]
            
            
    PAY_conf=confidence_check(PAY) #noqa:
    account_conf=confidence_check(account) #noqa:
    IFS_conf=confidence_check(IFS) #noqa:
    amount_conf=confidence_check(amount) #noqa:
    micr_conf=confidence_check(micr) #noqa:
    date_check(date) #noqa:
        
    if PAY_conf<80 or account_conf<80 or IFS_conf<80 or amount_conf<80:
        confidence_status="invalid"
    else:
        confidence_status="valid"
        
    print("Pay:", PAY)#noqa:
    print("From Account:", account)#noqa:
    print("IFS:", IFS)#noqa:
    print("Amount:", amount)#noqa:
    print("Date:", date)#noqa:
    print("MICR Staus:", micr_check(micr)[0])
    print("MICR Pincode:", micr_check(micr)[1])    
    print("MICR bankcode:", micr_check(micr)[2])        
    print("MICR branchcode:", micr_check(micr)[3])    
    print("PAYEE Confidence:",PAY_conf)
    print("Account Confidence:",account_conf)
    print("IFSC code confidence:",IFS_conf)
    print("Amount confidence:", amount_conf)
    print("MICR confidence:", micr_conf)
    print("Overall confidence:", confidence_status)    
    print("MICR:",micr)
    
    return {
        "pay_to": PAY, #noqa:
        "pay_confidence": PAY_conf,
        "payer_account": account,#noqa:
        "payer_account_confidence": account_conf,
        "ifsc_code": IFS,#noqa:
        "ifsc_code_confidence": IFS_conf,
        "amount": amount,#noqa:
        "amount_confidence": amount_conf,
        "date": date,#noqa:
        "date_status": date_check(date),#noqa:
        "micr_data": {
            "status": micr_check(micr)[0],
            "pincode": micr_check(micr)[1],
            "bank_code": micr_check(micr)[2],
            "branch_code": micr_check(micr)[3],
            },
        "micr": micr,
        "micr_confidence": micr_conf,
        "overall_confidence": confidence_status
            
            }
    
    
                
parse_data('Feb-23-2024_135700.json')

