from flask import (current_app, render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from ka.elasticsearch import INDEX_PREFIX
from ka.models import Score, Post, User, Measure, to_ordinal_string


search_app = Blueprint('search', __name__)


@search_app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    query = request.args.get('query').strip() if request.args.get('query') else ''
    scores, count = [], 0

    if query:
        scores, count = Score.search(query, 1, 20)
        unique_scores = { score.id: score for score in scores }  # TODO: unable to collapse on _id
        scores = unique_scores.values()

        index = INDEX_PREFIX + '*'
        # results = current_app.elasticsearch.search(
        #     index=index,
        #     body={
        #         'query': {
        #             'query_string': {
        #                 'query': query
        #             }
        #         },
        #     }
        # )
    #ids = [int(hit['_id']) for hit in search['hits']['hits']]
    #count = search['hits']['total']['value']
    #print(f'elasticsearch -> search doc with query {query} from {index}')
    #print(f"ids: {ids}, count {count}")

    return render_template(
        'search.html',
        title='Search',
        query=query,
        scores=scores
    )