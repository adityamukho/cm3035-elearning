from django.http import HttpResponse


def heartbeat(request):
    return HttpResponse("alive")
