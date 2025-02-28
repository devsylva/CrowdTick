from django.shortcuts import render
from rest_framework.response import Response
from django.core.cache import cache
from .models import Poll, Vote
from .serializers import PollSerializer, VoteSerializer, UserRegisterSerializer, UserLoginSerializer
from django.db import models
from .tasks import process_vote
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from django.contrib.auth import login
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        login(request, user)  # Sets sessionid
        request.session.modified = True
        request.session.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]  # Allow anyone to attempt login

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            login(request, user)  # Sets session cookie
            return Response({"detail": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"detail": "Login failed"}, status=status.HTTP_400_BAD_REQUEST)

# Create your views here.
class PollCreateView(generics.CreateAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)
    

class VoteCreateView(generics.CreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer

    def perform_create(self, serializer):
        poll_id = self.kwargs['pk']  # Get poll ID from URL
        try:
            poll = Poll.objects.get(id=poll_id)
            vote = serializer.save(user=self.request.user, poll=poll)  # Set poll and user
            process_vote.delay(vote.id)
            return Response({'message': 'Vote accepted, processing...'}, status=status.HTTP_202_ACCEPTED)
        except Poll.DoesNotExist:
            return Response({'detail': 'Poll not found'}, status=status.HTTP_404_NOT_FOUND)

class PollResultsView(generics.RetrieveAPIView):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def retrieve(self, request, *args, **kwargs):
        poll = self.get_object()
        cache_key = f"poll_{poll.id}_results"
        results = cache.get(cache_key)
        print(results)
        if not results:
            votes = Vote.objects.filter(poll=poll).values('choice').annotate(count=models.Count('choice'))
            results = {
                vote['choice']: vote['count'] for vote in votes
            }
            print(results)
            cache.set(cache_key, results, timeout=5)
        return Response(results, status=status.HTTP_200_OK)