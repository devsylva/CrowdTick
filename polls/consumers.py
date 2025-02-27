from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from .models import Poll

class PollConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.poll_id = self.scope['url_route']['kwargs']['poll_id']
        self.poll_group_name = f'poll_{self.poll_id}'

        # Join the poll group
        await self.channel_layer.group_add(
            self.poll_group_name,
            self.channel_name
        )
        await self.accept()

        # Send initial poll results on connect
        results = await self.get_poll_results()
        await self.send(text_data=json.dumps({'results': results}))

    async def disconnect(self, close_code):
        # Leave the poll group
        await self.channel_layer.group_discard(
            self.poll_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Optionally handle votes submitted via WebSocket
        data = json.loads(text_data)
        choice = data.get('choice')
        if choice:
            await self.save_vote(choice)

    async def poll_update(self, event):
        # Send updated poll results to the WebSocket client
        await self.send(text_data=json.dumps({
            'results': event['results'],
        }))

    @database_sync_to_async
    def get_poll_results(self):
        from .models import Poll, Vote
        # Fetch the current poll options (vote counts)
        poll = Poll.objects.get(id=self.poll_id)
        return poll.options

    @database_sync_to_async
    def save_vote(self, choice):
        from .models import Poll, Vote
        # Create a Vote object and trigger the Celery task
        from .tasks import process_vote
        user = self.scope['user']  # Requires AuthMiddlewareStack
        if user.is_authenticated:
            vote = Vote.objects.create(
                user=user,
                poll=Poll.objects.get(id=self.poll_id),
                choice=choice
            )
            process_vote.delay(vote.id)