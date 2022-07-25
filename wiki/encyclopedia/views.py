import random
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from markdown2 import Markdown

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}))

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    cyEntry = util.get_entry(title)
    if (cyEntry == None):
        return render(request, "encyclopedia/error.html")
    else:
        markdowner = Markdown()
        newEntry = markdowner.convert(cyEntry)
        return render(request, "encyclopedia/entry.html", {
            "newEntry": newEntry,
            "title":title
        })

def random(request):
    return entry(request, util.get_random_entry())

def search(request):
    if request.method=="POST":
        searchItem = request.POST.get('search')
        if (util.get_entry(searchItem) != None):
            return entry(request, searchItem)
        else:
            possibilities = util.re_search(searchItem)
            numPos = len(possibilities)
            return render(request, "encyclopedia/search.html", {
                "possibilities": possibilities,
                "numPos" : numPos
            })
    else:
        HttpResponse('Invalid Search Request')

def newpage(request):
    if request.method=="POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if (util.get_entry(title) != None):
                messages.error(request, "Title Already Exists!")
            else:
                util.save_entry(title, content)
                return entry(request, title)
        else:
            messages.error(request, "Error Saving Page - Invalid Input")
    return render(request, "encyclopedia/newpage.html", {
        "form": NewEntryForm()
    })

def editpage(request, title):
    if request.method=="POST":
        form = EditEntryForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title, content)
            return entry(request, title)
        else:
            messages.error(request, "Error Saving Page - Invalid Input")
            return render(request, "encyclopedia/editpage.html", {
                "form": EditEntryForm(request.POST),
                "title" : title
            })
    if request.method=="GET":
        gEntry = util.get_entry(title)
        if gEntry == None:
            return render(request, "encyclopedia/error.html")
        else:
            values = {"content" : gEntry}
            form = EditEntryForm(initial=values)
            return render(request, "encyclopedia/editpage.html", {
                "form": form,
                "title" : title
    })
