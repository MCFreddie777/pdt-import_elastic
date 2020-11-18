import jsonlines
import requests
import json
from os import path, listdir
from datetime import datetime
from config.connection import connection
from config.settings import DEBUG
from helpers.logging import Logging
from helpers.make_request import make_request


# parses each file of the files list
def parse_each_file(files, func):
    for index, file in enumerate(files):
        logging.log(f"Parsing file {file} ({index + 1}/{len(files)})")
        parse_file(file, func)


# parses each line of the file
def parse_file(file, func):
    with jsonlines.open(path.join(data_dir, file)) as reader:
        for obj in reader:
            func(obj)


# bulk index the tweet list
def index_tweets():
    def bulk_api_tweet_string(tweet, method):
        # id was removed from mapping
        id = tweet.pop('id')
        return f"{{\"{method}\":{{\"_id\":{id}}}}}\n{json.dumps(tweet)}"

    body = '\n'.join([bulk_api_tweet_string(tweet, 'index') for tweet in tweets]) + '\n'
    make_request(
        requests.post,
        url=f"http://{connection.hostname}:{connection.port}/{connection.index}/_bulk",
        headers={'Content-Type': 'application/json'},
        data=body
    )


# saves the tweet to the database
def save_tweet(obj):
    simplified_obj = dict()

    # dive into recursion until we hit the original tweet
    if 'retweeted_status' in obj and obj['retweeted_status'] is not None:
        simplified_obj['parent_id'] = save_tweet(obj['retweeted_status'])

    # tweet
    simplified_obj['id'] = obj['id_str']
    simplified_obj['content'] = obj['full_text']
    simplified_obj['retweet_count'] = obj['retweet_count']
    simplified_obj['favorite_count'] = obj['favorite_count']
    simplified_obj['happened_at'] = datetime.timestamp(datetime.strptime(obj['created_at'], '%a %b %d %H:%M:%S %z %Y'))

    # location
    if obj['coordinates'] and obj['coordinates']['coordinates']:
        simplified_obj['location'] = obj['coordinates']['coordinates']

    # author
    if obj['user'] is not None:
        simplified_obj['author'] = {
            "id": obj['user']['id'],
            "screen_name": obj['user']['screen_name'],
            "name": obj['user']['name'],
            "description": obj['user']['description'],
            "followers_count": obj['user']['followers_count'],
            "friends_count": obj['user']['friends_count'],
            "statuses_count": obj['user']['statuses_count']
        }

    # mentions
    if (obj['entities']['user_mentions']):
        simplified_obj['mentions'] = []
        for mentioned_user in obj['entities']['user_mentions']:
            simplified_obj['mentions'].append({
                "id": mentioned_user['id'],
                "screen_name": mentioned_user['screen_name'],
                "name": mentioned_user['name'],
            })

    # country
    if (
            obj['place'] is not None and
            obj['place']['country_code'] and
            obj['place']['country']
    ):
        simplified_obj['country'] = {
            "code": obj['place']['country_code'],
            "name": obj['place']['country']
        }

    # hashtags
    if (
            obj['entities'] is not None and
            obj['entities']['hashtags'] is not None and
            len(obj['entities']['hashtags'])
    ):
        simplified_obj['hashtags'] = []
        for hashtag in obj['entities']['hashtags']:
            simplified_obj['hashtags'].append(hashtag['text'])

    # append the simplified object into tweet list
    tweets.append(simplified_obj)

    # if the tweet limit is reached, bulk index the tweet list
    if len(tweets) >= tweet_bulk_limit:
        index_tweets()
        tweets.clear()

    return obj['id_str']


# resolve relative paths
data_dir = path.join(path.dirname(__file__), '../data')

# global object for logging
logging = Logging(datetime.now())

# list to store the tweets until bulk-indexed
tweets = []
tweet_bulk_limit = 1000

if DEBUG:
    file = 'test/test_2000.jsonl'
    logging.log(f"Parsing file {file}")
    parse_file(file, save_tweet)
else:
    files = (entry for entry in listdir(data_dir) if entry.endswith('.jsonl'))
    parse_each_file(list(files), save_tweet)

# bulk index the rest of tweets in the list
if len(tweets):
    index_tweets()

logging.log("Parsing finished.")
