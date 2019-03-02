from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.index,name='Twitter_Analysis'),

    path('teams/chart',views.teams,name='Teams'),

    path('teams/tweets', views.teams_tweets, name='Teams Tweets'),
    
    path('get_timeline_tweets/',views.get_timeline_tweets,name='Twitter_Analysis'),

    path('top_ten_tweets/<str:team_tag>/',views.top_ten_tweets,name='Top Ten Tweets'),

    path('plot_team_sentiments/<str:team_tag>/',views.plot_team_sentiments,name='Top Ten Tweets'),

]