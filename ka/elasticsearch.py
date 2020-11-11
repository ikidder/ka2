from flask import current_app

# based on https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search

INDEX_PREFIX = 'ka-'


def add_to_index(index, model):
    if not current_app.elasticsearch:
        print('no elasticsearch found in current_app')
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    result = current_app.elasticsearch.index(index=index, id=model.id, body=payload)
    print(f'elasticsearch -> indexing doc with id {model.id} into {index}')
    print(result)


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        print('no elasticsearch found in current_app')
        return
    result = current_app.elasticsearch.delete(index=index, id=model.id)
    print(f'elasticsearch -> deleting doc with id {model.id} from {index}')
    print(result)


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        print('no elasticsearch found in current_app')
        return [], 0
    search = current_app.elasticsearch.search(
        index=index,
        body={
            'query': {
                'multi_match': {
                    'query': query,
                    'fields': ['*']
                }
            },
            'from': (page - 1) * per_page,
            'size': per_page
        }
    )
    ids = [int(hit['_id']) for hit in search['hits']['hits']]
    print(f'elasticsearch -> search doc with query {query} from {index}')
    print(f"ids: {ids}, count {search['hits']['total']['value']}")
    return ids, search['hits']['total']['value']




# def search(query, page, per_page):
#     if not current_app.elasticsearch:
#         return [], 0
#     es = current_app.elasticsearch
#     result = es.search(
#         index=INDEX,
#         body={'query':
#                   {'multi_match':
#                        {'query': query,
#                         'type': 'bool_prefix',
#                         'fields': ['_name', '_content'],
#                         'tie_breaker': 0.3
#                         }
#                    },
#               'from': (page - 1) * per_page,
#               'size': per_page
#               }
#     )
#     ids = [int(hit['_id']) for hit in result['hits']['hits']]
#
#     return ids, result['hits']['total']['value']


# index definition
"""
PUT /ka-objects
{
  "settings": {
    "analysis": {
      "filter": {
        "autocomplete_filter": {
          "type": "edge_ngram",
          "min_gram": 2,
          "max_gram": 10
        }
      },
      "analyzer": {
        "autocomplete": { 
          "type": "custom",
          "tokenizer": "standard",
          "filter": [
            "lowercase",
            "autocomplete_filter"
          ]
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "_name": {
        "type": "text",
        "analyzer": "autocomplete", 
        "search_analyzer": "standard" 
      },
      "_content": {
        "type": "text",
        "analyzer": "autocomplete", 
        "search_analyzer": "standard" 
      }
    }
  }
}"""