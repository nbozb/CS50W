from django.shortcuts import render
import datetime


def index(request):
    now = datetime.datetime.now()
    return render(request, "newyear/index.html", {
        "newyear": now.month == 1 & now.day == 1
    })
