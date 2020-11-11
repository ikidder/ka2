import os
from ka import *
from ka.models import *
from sqlalchemy.dialects import postgresql

app = create_app()
ctx = app.test_request_context()
ctx.push()

environment_vars = [k for k, v in os.environ.items()]


def get_sql(q):
    return str(q.statement.compile(dialect=postgresql.dialect()))


print()
print('*' * 15)
print('Environment Variables: ', environment_vars)
print('Current Directory: ', os.getcwd())
print()
print('IMPORTANT: remember to trigger the request teardown')
print('see: https://flask.palletsprojects.com/en/1.1.x/shell/')
print('-> app.process_response(app.response_class())')
print('-> ctx.pop()')
print()
print('To see the SQl underlying a query: ')
print('print(get_sql(q))')
print('where q = Session.query(whatever) . . . ')
print('*' * 15)