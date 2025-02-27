from celery import shared_task
from .models import Poll, Vote
from django.core.cache import cache 

@shared_task
def process_vote(voteid):
    try:
        vote = Vote.objects.get(id=voteid)
        poll = vote.poll
        #update poll option (increment vote count)
        if vote.choice in poll.options:
            poll.options[vote.choice] += 1
            poll.save()
            #delete cache
            cache_key = f"poll_{poll.id}_results"
            cache.delete(cache_key) 
    except Vote.DoesNotExist:
        pass  # hanlde silently for now