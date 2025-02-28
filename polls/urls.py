from django.urls import path
from . import views

urlpatterns = [
    path("api/polls/", views.PollCreateView.as_view(), name="polls"),
    path("api/polls/<int:pk>/vote/", views.VoteCreateView.as_view(), name="votes"),
    path("api/polls/<int:pk>/results/", views.PollResultsView.as_view(), name="poll_results"),
    path('api/register/', views.RegisterView.as_view(), name='register'),
]