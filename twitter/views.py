import sys
from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import tweepy
from textblob import TextBlob
from operator import itemgetter
from matplotlib.figure import Figure
import io
import matplotlib.pyplot as plt;

plt.rcdefaults()


# Home Page
def index(request):
    return render(request, 'index.html')


# IPL Teams for tweets
def teams(request):
    teams = {"CSK": "https://pbs.twimg.com/profile_banners/117407834/1548912860/1500x500",
             "RCB": "https://pbs.twimg.com/profile_banners/70931004/1545231901/1500x500",
             "KKR": "https://pbs.twimg.com/profile_banners/23592970/1545163646/1500x500",
             "KXIP": "https://pbs.twimg.com/profile_banners/30631766/1548675483/1500x500",
             "MumbaiIndians": "https://pbs.twimg.com/profile_banners/106345557/1545202853/1500x500",
             "SRH": "https://pbs.twimg.com/profile_banners/989137039/1545149246/1500x500",
             "rajasthanroyals": "https://pbs.twimg.com/profile_banners/17082958/1549798220/1500x500",
             "ThisIsNewDelhi": "https://pbs.twimg.com/profile_banners/176888549/1550919708/1500x500"}
    return render(request, 'pages/chart-for-teams.html', {"context": teams})


# IPL Teams for pie charts
def teams_tweets(request):
    teams = {"CSK": "https://pbs.twimg.com/profile_banners/117407834/1548912860/1500x500",
             "RCB": "https://pbs.twimg.com/profile_banners/70931004/1545231901/1500x500",
             "KKR": "https://pbs.twimg.com/profile_banners/23592970/1545163646/1500x500",
             "KXIP": "https://pbs.twimg.com/profile_banners/30631766/1548675483/1500x500",
             "MumbaiIndians": "https://pbs.twimg.com/profile_banners/106345557/1545202853/1500x500",
             "SRH": "https://pbs.twimg.com/profile_banners/989137039/1545149246/1500x500",
             "rajasthanroyals": "https://pbs.twimg.com/profile_banners/17082958/1549798220/1500x500",
             "ThisIsNewDelhi": "https://pbs.twimg.com/profile_banners/176888549/1550919708/1500x500"}
    return render(request, 'pages/tweets-for-team.html', {"context": teams})


# Getting twitter credentials
def get_twitter_auth():
    try:
        CONSUMER_KEY = settings.TWITTER_CONSUMER_KEY
        CONSUMER_SECRET = settings.TWITTER_CONSUMER_SECRET
        ACCESS_TOKEN = settings.TWITTER_ACCESS_TOKEN
        ACCESS_KEY = settings.TWITTER_ACCESS_KEY
    except KeyError:
        sys.stderr.write("TWITTER ENV VARIABLE NOT SET \n")
        sys.exit(1)
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_KEY)
    return auth


# Getting twitter client auth
def get_twitter_client():
    auth = get_twitter_auth()
    client = tweepy.API(auth)
    return client


# Getting tweets with matching hashtag
def get_hashtag_tweets(request, team_tag):
    client = get_twitter_client()
    positive = 0
    negative = 0
    neutral = 0
    overall_polarity = 0
    overall_tweet_sentiment = ''
    how_many_tweets = 100
    search_text = "#" + team_tag
    tweets_data = []
    tweets_data_json = {}
    tweets_data_json_list = []
    tweets_data_list = []
    try:
        for page in tweepy.Cursor(client.search, q=search_text, count=200, since="2018-12-01").items(
                how_many_tweets):
            tweets_data_dict = {}
            blob = TextBlob(page._json['text'])
            for sentence in blob.sentences:
                overall_polarity += sentence.sentiment.polarity
                tweet_polarity = sentence.sentiment.polarity
                if (tweet_polarity == 0 or 0.00 or 0.0):
                    neutral += 1
                elif (tweet_polarity < 0 or 0.00 or 0.0):
                    negative += 1
                elif (tweet_polarity > 0 or 0.00 or 0.0):
                    positive += 1
            if positive > negative:
                overall_tweet_sentiment = "POSITIVE"
            elif negative > positive:
                overall_tweet_sentiment = "NEGATIVE"
            elif negative == positive:
                overall_tweet_sentiment = "NEUTRAL"
            tweets_data_dict['created_at'] = page._json['created_at']
            tweets_data_dict['tweet'] = page._json['text']
            tweets_data_dict['polarity'] = tweet_polarity
            tweets_data_dict['urls'] = page._json['entities']['urls']
            tweets_data_dict['lang'] = page._json['lang']
            tweets_data_list.append(tweets_data_dict)
        tweets_data.append(tweets_data_list)
        tweets_data_json['total_tweets'] = positive + negative + neutral
        tweets_data_json['positive_percentage'] = percentage(positive, tweets_data_json['total_tweets'])
        tweets_data_json['negative_percentage'] = percentage(negative, tweets_data_json['total_tweets'])
        tweets_data_json['neutral_percentage'] = percentage(neutral, tweets_data_json['total_tweets'])
        tweets_data_json['overall_tweet_sentiment'] = overall_tweet_sentiment
        tweets_data_json_list.append(tweets_data_json)
        tweets_data.append(tweets_data_json_list)
    except tweepy.error.TweepError as et:
        print(et)
    except Exception as e:
        print(e)
    return tweets_data


# Getting top ten tweets
def top_ten_tweets(request, team_tag):
    data = get_hashtag_tweets(request, team_tag)
    top_tweets = sorted(data[0], key=itemgetter('polarity'), reverse=True)
    top_ten_tweets = top_tweets[0:10]
    return render(request, 'tweets/top-ten-tweets.html', {"data": top_ten_tweets})


# Plotting sentiments of tweets
def plot_team_sentiments(request, team_tag):
    data = get_hashtag_tweets(request, team_tag)
    top_tweets = sorted(data[0], key=itemgetter('polarity'), reverse=True)
    top_ten_tweets = top_tweets[0:10]
    positive_percentage = data[1][0]['positive_percentage']
    negative_percentage = data[1][0]['negative_percentage']
    neutral_percentage = data[1][0]['neutral_percentage']
    overall_tweet_sentiment = data[1][0]['overall_tweet_sentiment']
    labels = ['Positive[' + str(positive_percentage) + '%]', 'Negative[' + str(negative_percentage) + '%]',
              'Neutral[' + str(neutral_percentage) + '%]']
    sizes = [positive_percentage, negative_percentage, neutral_percentage]
    fig = Figure()
    # canvas = FigureCanvas(fig)
    colors = ['#FFA500', '#FFD700', '#DAA520']
    patches, texts = plt.pie(sizes, colors=colors, startangle=90)
    plt.legend(patches, labels, loc="best")
    plt.title("Sentiment of " + team_tag + " Team")
    plt.axis('equal')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close(fig)
    # plt.show()
    response = HttpResponse(buf.getvalue(), content_type='image/png')
    return response


# Getting tweets from timeline
def get_timeline_tweets(request):
    client = get_twitter_client()
    tweets_data = []
    for status in tweepy.Cursor(client.home_timeline).items(10):
        tweets_data.append(status.text)
    print(tweets_data[0])
    return render(request, 'tweets/timeline_tweets.html', {"data": tweets_data})


# Calculating Sentiments Percentage
def percentage(part, whole):
    return 100 * float(part) / float(whole)
