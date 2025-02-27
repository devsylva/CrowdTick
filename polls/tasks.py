from celery import shared_task
from django.core.cache import cache 
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def process_vote(voteid):
    try:
        from .models import Poll, Vote
        vote = Vote.objects.get(id=voteid)
        poll = vote.poll
        #update poll option (increment vote count)
        if vote.choice in poll.options:
            poll.options[vote.choice] += 1
            poll.save()
            #delete cache
            cache_key = f"poll_{poll.id}_results"
            cache.delete(cache_key) 

            #Notify websocket group
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'poll_{poll.id}',
                {
                    'type': 'poll_update',
                    'results': poll.options
                }
            )
    except Vote.DoesNotExist:
        pass  # hanlde silently for now