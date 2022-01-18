import config
from models import ES


def movie_mapping():
    return {
        "mappings": {
            "properties": {
                "director": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "genres": {
                    "properties": {
                        "title": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword",
                                    "ignore_above": 256
                                }
                            }
                        }
                    }
                },
                "id": {
                    "type": "long"
                },
                "imdb_score": {
                    "type": "float"
                },
                "name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword",
                            "ignore_above": 256
                        }
                    }
                },
                "popularity": {
                    "type": "float"
                }
            }
        }
    }


def fuzzy_search(query, fields, size=10):
    body = {
        "size": size,
        "sort": [{"popularity": {"order": "desc"}}],
        "query": {
            "multi_match": {"fields": fields, "query": query, "fuzziness": "AUTO"}
        },
    }
    return ES.search(index=config.ES_INDEX, body=body)
