from rds import client
from django.shortcuts import render, redirect
from django import forms

def show(request):
    context = {}
    message = request.GET.get('message', '')
    if message != '':
        context['message'] = message

    error = request.GET.get('error', '')
    if error != '':
        context['error'] = error

    db = client.OcdDB()
    result = db.get_records()
    context['records'] = result
    return render(request, 'teller.html', context)

class NameForm(forms.Form):
    your_name = forms.CharField(label="Your name", max_length=100)

def update_details(request, id=None):
    if request.method == "POST":
        pay_to = request.POST.get('pay_to', '')
        issued_on = request.POST.get('issued_on', '')
        payer_acc = request.POST.get('payer_acc', '')
        amt = request.POST.get('amt', '')
        ifsc = request.POST.get('ifsc', '')
        micr_pin = request.POST.get('micr_pin', '')
        micr_bank = request.POST.get('micr_bank', '')
        micr_branch = request.POST.get('micr_branch', '')
        micr_branch = request.POST.get('micr_branch', '')
        print("issued_on :: ", issued_on)
        db = client.OcdDB()
        result = db.update_record(id, pay_to, issued_on, payer_acc, amt, ifsc, micr_pin, micr_bank, micr_branch)
    context = {}
    return redirect('/teller/dashboard', 'teller.html', context)

def change_status(request, id=None, action=None):
    if id is None:
        return redirect('/teller/dashboard?error=no id provided', 'teller.html', {'error':'no id provided'})
    if action is None:
        return redirect('/teller/dashboard?error=no action provided', 'teller.html', {'error':'no action provided'})
    
    context = {}
    db = client.OcdDB()
    result = db.update_status(id, action)
    msg_str = ''
    if result is False:
        msg_str = '?error=unable to update the record at the moment'
    else:
        msg_str = '?message=record updated successfully'
    return redirect(f'/teller/dashboard{msg_str}', 'teller.html', context)