from django.shortcuts import render
from django.http import HttpResponse
from lists.models import Item

# Create your views here.


def home_page(request):
    # Todo: Don't save a blank item for every request
    item = Item()
    item.text = request.POST.get('item_text', '')
    item.save()

    context = {'new_item_text': item.text}
    # Todo: Display multiple items in the table
    return render(request, 'home.html', context)
