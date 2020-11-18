import requests
from config.connection import connection
from helpers.make_request import make_request


def get_index(name):
    response = make_request(
        requests.get,
        fail_on_status_code=False,
        url=f"http://{connection.hostname}:{connection.port}/{name}/",
    )

    return response


def remove_index_if_exists(name):
    if get_index(name).ok:
        make_request(
            requests.delete,
            url=f"http://{connection.hostname}:{connection.port}/{name}/",
        )


def create_index(name, settings):
    make_request(
        requests.put,
        url=f"http://{connection.hostname}:{connection.port}/{name}/",
        json=settings
    )


tweet_settings = {
    "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 2
    }
}

tweet_mapping = {
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "author": {
                "properties": {
                    "description": {
                        "type": "text"
                    },
                    "followers_count": {
                        "type": "integer"
                    },
                    "friends_count": {
                        "type": "integer"
                    },
                    "id": {
                        "type": "long"
                    },
                    "name": {
                        "type": "text"
                    },
                    "screen_name": {
                        "type": "text"
                    },
                    "statuses_count": {
                        "type": "integer"
                    }
                }
            },
            "content": {
                "type": "text"
            },
            "country": {
                "properties": {
                    "code": {
                        "type": "keyword"
                    },
                    "name": {
                        "type": "text"
                    }
                }
            },
            "favorite_count": {
                "type": "integer"
            },
            "happened_at": {
                "type": "date"
            },
            "hashtags": {
                "type": "text"
            },
            "id": {
                "type": "keyword"
            },
            "location": {
                "type": "geo_point"
            },
            "mentions": {
                "properties": {
                    "id": {
                        "type": "long"
                    },
                    "name": {
                        "type": "text"
                    },
                    "screen_name": {
                        "type": "text"
                    }
                }
            },
            "parent_id": {
                "type": "keyword"
            },
            "retweet_count": {
                "type": "integer"
            }
        }
    }
}

# remove all documents from index
remove_index_if_exists(name=connection.index)

# create index with mappings
create_index(name=connection.index, settings={**tweet_settings, **tweet_mapping})
