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
        "number_of_replicas": 0, # memory issues
        "index": {
            "max_ngram_diff": 9
        },
        "analysis": {
            "analyzer": {
                "englando": {
                    "filter": [
                        "english_possessive_stemmer",
                        "lowercase",
                        "english_stop",
                        "english_stemmer"
                    ],
                    "char_filter": [
                        "html_strip"
                    ],
                    "tokenizer": "standard"
                },
                "custom_ngram": {
                    "filter": [
                        "lowercase",
                        "asciifolding",
                        "filter_ngrams"
                    ],
                    "char_filter": [
                        "html_strip"
                    ],
                    "tokenizer": "standard"
                },
                "custom_shingles": {
                    "filter": [
                        "asciifolding",
                        "filter_shingles"
                    ],
                    "char_filter": [
                        "html_strip"
                    ],
                    "tokenizer": "standard"
                }
            },
            "filter": {
                "english_possessive_stemmer": {
                    "type": "stemmer",
                    "language": "possessive_english"
                },
                "english_stop": {
                    "type": "stop",
                    "stopwords": "_english_"
                },
                "english_stemmer": {
                    "type": "stemmer",
                    "language": "english"
                },
                "filter_ngrams": {
                    "type": "ngram",
                    "min_gram": 1,
                    "max_gram": 10
                },
                "filter_shingles": {
                    "type": "shingle",
                    "token_separator": ""
                }
            }
        }
    }
}

tweet_mapping = {
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "author": {
                "properties": {
                    "description": {
                        "type": "text",
                        "analyzer": "englando",
                        "fields": {
                            "custom_shingles": {
                                "type": "text",
                                "analyzer": "custom_shingles"
                            }
                        }
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
                        "type": "text",
                        "fields": {
                            "custom_ngram": {
                                "type": "text",
                                "analyzer": "custom_ngram"
                            },
                            "custom_shingles": {
                                "type": "text",
                                "analyzer": "custom_shingles"
                            }
                        }
                    },
                    "screen_name": {
                        "type": "text",
                        "fields": {
                            "custom_ngram": {
                                "type": "text",
                                "analyzer": "custom_ngram"
                            }
                        }
                    },
                    "statuses_count": {
                        "type": "integer"
                    }
                }
            },
            "content": {
                "type": "text",
                "analyzer": "englando"
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
            "location": {
                "type": "geo_point"
            },
            "mentions": {
                "properties": {
                    "id": {
                        "type": "long"
                    },
                    "name": {
                        "type": "text",
                        "fields": {
                            "custom_ngram": {
                                "type": "text",
                                "analyzer": "custom_ngram"
                            },
                            "custom_shingles": {
                                "type": "text",
                                "analyzer": "custom_shingles"
                            }
                        }
                    },
                    "screen_name": {
                        "type": "text",
                        "fields": {
                            "custom_ngram": {
                                "type": "text",
                                "analyzer": "custom_ngram"
                            }
                        }
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
