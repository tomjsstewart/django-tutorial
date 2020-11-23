from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.views import generic
from django.db.models import F

from .models import Question, Choice


class IndexView(generic.ListView):
    template_name = 'polls/index.html'
    context_object_name = 'latest_question_list'


    def get_queryset(self):
        """ Return the last 5 published questions """
        return Question.objects.order_by('-pub_date')[:5]
    

class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


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