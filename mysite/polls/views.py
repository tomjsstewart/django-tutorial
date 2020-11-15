from django.http import HttpResponse
from django.shortcuts import render

from .models import Question



def index(request):
    # Get the 5 most recent questions
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # Context is a dictionary mapping template variable names to python objects
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    return HttpResponse(f"You're looking at question {question_id}.")

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)
