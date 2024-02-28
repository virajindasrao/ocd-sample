from django.shortcuts import render
from rds import client

def show(request, id=None):
    context = {}
    if id != '':
        db = client.OcdDB()
        result = db.track_record(id)

        status_map = {
            "pending":0,
            "approved":1,
            "rejected":2,
            "clearing":3,
            "realization":4,
            "realized":5,
            "cleared":6
        }

        try:
            context['status_code'] = status_map[result[0].status]
        except Exception as e:
            context['status_code'] = 0
    return render(request, 'diagram.html', context)


def generate(request):
    actor_name = request.GET.get('actor_name')
    