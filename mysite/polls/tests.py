import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from .models import Question, Choice



def create_question(question_text, days):
    """
    Create a question with the given `question_text` and published the
    given number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


def create_choice(question, choice_text):
    """
    Create a choice with the given `question_text` and 0 votes for the given
    question. 
    """
    return Choice.objects.create(question=question, choice_text=choice_text, votes=0)



def create_question_and_choice(question_text, days, choice_text=None):
    """
    Create a question and a corresponding choice, since all questions must
    have a choice to be displayed.

    If unspecified `choice_text` will be `f"{question_text} -- choice"`

    returns a (`Question`, `Choice`) pair
    """
    q = create_question(question_text=question_text, days=days)
    choice_text = f"{question_text} -- choice" if choice_text is None else choice_text
    c = create_choice(q, choice_text=choice_text)
    return q, c


class QuestionModelTests(TestCase):

    def test_was_published_recently_with_future_question(self):
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_future_question2(self):
        time = timezone.now() + datetime.timedelta(seconds=1)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        `was_published_recently()` returns `False` for questions whose `pub_date`
        is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
            """
            `was_published_recently()` returns `True` for questions whose `pub_date`
            is within the last day.
            """
            time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
            recent_question = Question(pub_date=time)
            self.assertIs(recent_question.was_published_recently(), True)


class QuestionIndexViewTests(TestCase):
    ## Note that the database is reset with each test method so no changes to the db
    ## persist beyond the test function

    def test_no_questions(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_past_question(self):
        """
        Questions with a `pub_date` in the past are displayed on the index page
        """
        create_question_and_choice(question_text='Past Question', days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
            ['<Question: Past Question>']
        )

    def test_future_question(self):
        """
        Questions with a `pub_date` in the future are not displayed on the index page
        """
        create_question_and_choice(question_text='Future Question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls are available.')
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_and_past_question(self):
        """
        Even if both past and future questions exist, only past questions
        are displayed.        
        """
        create_question_and_choice(question_text='Past Question', days=-30)
        create_question_and_choice(question_text='Future Question', days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
            ['<Question: Past Question>']
        )

    def test_two_past_questions(self):
        """
        The questions index page may display multiple questions.
        """
        create_question_and_choice(question_text="Past question 1", days=-30)
        create_question_and_choice(question_text="Past question 2", days=-5)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['latest_question_list'],
            ['<Question: Past question 2>', '<Question: Past question 1>']
        )
    
    def test_question_with_no_choice(self):
        create_question(question_text="No Choices", days=-3)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], [])
    
    def test_question_with_one_choice(self):
        create_question_and_choice(question_text="One choice", days=-3, choice_text="Choice #1")
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'],
        ['<Question: One choice>'])
    
    def test_two_questions_one_with_one_without_choice(self):
        create_question_and_choice(question_text="Choice question",
                        days=-2, choice_text="Choice #1")
        create_question(question_text="No choice question", days=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], 
        ['<Question: Choice question>'])
    
    def test_two_questions_one_with_choices_one_without_choice(self):
        q, _ = create_question_and_choice(question_text="Choice question",
                        days=-2, choice_text="Choice #1")
        for x in range(2, 10):
            create_choice(q, f"Choice #{x}")
        create_question(question_text="No choice question", days=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(response.context['latest_question_list'], 
        ['<Question: Choice question>'])



class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 not found.
        """
        future_question = create_question("Future question", days=30)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
    
    def test_past_question(self):
        """
        The detail view of a question with a pub_date in the past
        displays questions text.
        """
        past_question = create_question("Past question", days=-30)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, "Past question")