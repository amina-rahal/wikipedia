from django.shortcuts import render,redirect
from markdown2 import Markdown 
from django import forms
from django.contrib import messages
from random import randint

from . import util

class NewEntryForm(forms.Form):
    title = forms.CharField(
        required=True,
        label="",
        widget=forms.TextInput(
            attrs={"placeholder": "Title", "class": "mb-4"}
        ),
    )
    content = forms.CharField(
        required=True,
        label="",
        widget=forms.Textarea(
            attrs={
                "class": "form-control mb-4",
                "placeholder": "Content (markdown)",
                "id": "new_content",
            }
        ),
    )

markdown = Markdown()

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entries = util.list_entries()

    if title not in entries:
        return render(request, "encyclopedia/error.html", {
            'code': '404',
            'error': 'Entry not found!'
        })

    content = util.get_entry(title)
    entry = markdown.convert(content)

    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "entry": entry
    })

def search(request):

    entries = util.list_entries()

    search = request.GET.get("q", "")

    if search is None or search == "":
        return render(request,"encyclopedia/search.html", {
            "result": "", 
            "query": search
    })

    result = [entry for entry in entries if search.lower() in entry.lower()]

    if len(result) == 1 and search.lower() == result[0].lower():
        return redirect('entry', result[0])

    return render(request, 'encyclopedia/search.html', {
        'result': result,
        'query': search
    })

def new(request):

    if request.method == "GET":
        return render(request, 'encyclopedia/new.html', {
            'form': NewEntryForm()
        })
    
    form = NewEntryForm(request.POST)

    if form.is_valid():

        title = form.cleaned_data.get('title')
        content = form.cleaned_data.get('content')

        if title.lower() in [entry.lower() for entry in util.list_entries()]:
            messages.add_message(
                request,
                messages.WARNING,
                message=f'Entry "{title}" already exists',
            )
        else:
            with open(f"entries/{title}.md", "w") as file:
                file.write(content)
            return redirect("entry", title)
    else:
        messages.add_message(
            request, messages.WARNING, message='Invalid request form'
        )
    return render(request, 'encyclopedia/new.html', {
        'form': form
    })

def edit(request, entry):
    if request.method == "GET":
        title = entry
        content = util.get_entry(title)
        form = NewEntryForm({"title": title, "content": content})
        return render(
            request,
            "encyclopedia/edit.html",
            {"form": form, "title": title},
        )

    form = NewEntryForm(request.POST)
    if form.is_valid():
        title = form.cleaned_data.get("title")
        content = form.cleaned_data.get("content")

        util.save_entry(title=title, content=content)
        return redirect("entry", title)

def random_entry(request):
    entries = util.list_entries()
    entry = entries[randint(0, len(entries) - 1)]
    return redirect("entry", entry)


