from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

from django.db.models import F

from .models import Question, Choice



def index(request):
    # Get the 5 most recent questions
    latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # Context is a dictionary mapping template variable names to python objects
    context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html', context)

def detail(request, question_id):
    # get_object_or_404 will attemps the get on the Question model
    # -- get Question with pk=question_id
    # function will raise a Http404 if the object does not exist
    question = get_object_or_404(Question, pk=question_id)
    context = {'question': question}
    return render(request, 'polls/detail.html', context)

def results(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    contxt = {'question': question}
    return render(request, 'polls/results.html', context=contxt)

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        print(request.POST)
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form
        context = {'question': question, 'error_message': "You didn't select a choice"}
        return render(request, 'polls/detail.html', context=context)
    else:
        # This generates SQL to run on the Db and python never loads the value of votes
        # thus we avoid any possibility of a race condition occuring with 2 threads reading 
        # the same value and both incrementing and saving, so that only one threads work is
        # saved.
        selected_choice.votes = F('votes') +1
        # At this point the db actually updates the value
        selected_choice.save()
        # should we wish to actually update the value stored in selected_choice.votes we
        # must run
        # Additionally this F persists after the save, so running save() twice would increment 
        # the value twice
        selected_choice.refresh_from_db()

        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))