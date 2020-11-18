import jsonlines
import requests
from os import path, listdir
from config.connection import connection
from datetime import datetime


# parses each file of the files list
def parse_each_file(files, func):
    for index, file in enumerate(files):
        parse_file(file, func)


# parses each line of the file
def parse_file(file, func):
    with jsonlines.open(path.join(data_dir, file)) as reader:
        for obj in reader:
            func(obj)


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

    response = requests.post(
        url=f"http://{connection.hostname}:{connection.port}/{connection.index}/_doc",
        json=simplified_obj
    )

    if (response.status_code >= 300):
        raise Exception(response.content.decode())

    return obj['id_str']

# debug mode
DEBUG = False

# resolve relative paths
data_dir = path.join(path.dirname(__file__), '../data')

if DEBUG:
    parse_file(path.join(data_dir, 'test/test_1.jsonl'), save_tweet)
else:
    files = (entry for entry in listdir(data_dir) if entry.endswith('.jsonl'))
    parse_each_file(list(files), save_tweet)
