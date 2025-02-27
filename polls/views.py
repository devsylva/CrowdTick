from django.shortcuts import render
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from django.core.cache import cache
from .models import Poll, Vote
from .serializers import PollSerializer, VoteSerializer

# Create your views here.
class PollCreateView(generics.CreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def perform_create(self, serializer):
        queryset = Poll.objects.all()
        serializer.save(creator=self.request.user)
    

class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    def perform_create(self, serializer):
        vote = serializer.save(user=self.request.user)
        process_vote.delay(vote.id) # Queue the task
        return Response({'message': 'Vote accepted, processing...'}, status=status.HTTP_202_ACCEPTED)

class PollResultsView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def retrieve(self, request, *args, **kwargs):
        poll = self.get_object()
        cache_key = f"poll_{poll.id}_results"
        results = cache.get(cache_key)
        if not results:
            votes = Vote.objects.filter(poll=poll).values('choice').annotate(count=models.Count('choice'))
            results = {
                vote['choice']: vote['count'] for vote in votes
            }
            cache.set(cache_key, results, timeout=5)
        return Response(results, status=status.HTTP_200_OK)