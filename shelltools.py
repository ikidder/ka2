import os
from ka import *
from ka.models import *

app = create_app()
ctx = app.test_request_context()
ctx.push()

environment_vars = [k for k, v in os.environ.items()]

print()
print('*' * 15)
print('Current Directory: ', os.getcwd())
print('Environment Varibles: ')
for k, v in os.environ.items():
    print(k, ': ', v)
print()
print('IMPORTANT: remember to trigger the request teardown')
print('see: https://flask.palletsprojects.com/en/1.1.x/shell/')
print('-> app.process_response(app.response_class())')
print('-> ctx.pop()')
print()
print('*' * 15)

from ka.tests.makers import *