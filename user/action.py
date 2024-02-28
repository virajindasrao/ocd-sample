from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import time
from . import files
from textract import process
import base64
from rds import client
# from rds import client


def upload_cheque(request):
    context = {}
    image_uploaded = False

    t = time.localtime()
    file_name = time.strftime('%m%d%Y%H%M%S', t)

    reference = request.GET.get('reference', '')
    print(f"reference {reference}")

    if request.method == "GET" and reference != '':
        db = client.OcdDB()
        result = db.track_record(reference)
        print(result)

        if result is False or result == []:
            context['track_error'] = "Not able to detect the reference at the moment. Make sure you enter the number correctly."
        else:
            context['track_message'] = f"The status of the reference is {result[0].get('status')}"

    if request.method == "POST":
        cheque_image = request.FILES['cheque']
        ext = request.FILES['cheque'].name.split('.')[1]
    
        if files.upload(cheque_image, f'{file_name}.{ext}') is False:
            context['error'] = 'Failed to submit transaction. Kindly try again!'
            return render(request, 'user.html', context)

        if process.convert(f'{file_name}.{ext}', f'{file_name}.json') is False:
            context['error'] = 'Failed to submit transaction. Kindly try again!'
            return render(request, 'user.html', context)
        
        payee_name = request.POST.get('payee_name', '')
        payee_account = request.POST.get('payee_account', '')
        contact_number = request.POST.get('contact_number', '')
        
        d = process.extract(file_name)
        print("data :: ", d)

        transition = 'pending'

        if 'pay_to' not in d:
            d['pay_confidence'] = 0
            d['pay'] = ''

        if 'payer_account' not in d:
            d['payer_account_confidence'] = 0
            d['payer_account'] = ''

        if 'ifsc_code' not in d:
            d['ifsc_code_confidence'] = 0
            d['ifsc_code'] = ''

        if 'amount' not in d:
            d['amount_confidence'] = 0
            d['amount'] = ''

        if 'micr' not in d:
            d['micr_confidence'] = 0
            d['micr'] = ''

        overall_confidence = d['pay_confidence'] + d['payer_account_confidence'] + d['ifsc_code_confidence'] + d['amount_confidence'] + d['micr_confidence']
        overall_confidence = overall_confidence / 5

        db = client.OcdDB()
        result = db.insert_record('pending', 
                                  d['pay_to'], 
                                  d['pay_confidence'], 
                                  d['payer_account'], 
                                  d['payer_account_confidence'], 
                                  d['ifsc_code'], 
                                  d['ifsc_code_confidence'], 
                                  d['amount'], 
                                  d['amount_confidence'], 
                                  d['date'], 
                                  d['date_status'], 
                                  d['micr'], 
                                  d['micr_confidence'], 
                                  d['micr_data']['status'], 
                                  d['micr_data']['pincode'], 
                                  d['micr_data']['bank_code'], 
                                  d['micr_data']['branch_code'], 
                                  overall_confidence, 
                                  f'{file_name}.png', 
                                  f'{file_name}.json',
                                  d['signature_data']['present'],
                                  d['signature_data']['count'],
                                  payee_name,
                                  payee_account,
                                  contact_number,
                                  file_name)
        if result is False:
            context['error'] = "error occured. Kindly try later."
        else:
            context['message'] = f'Cheque has been submitted for review. Kindly use this number for tracking [{file_name}]'

    return render(request, 'user.html', context)

