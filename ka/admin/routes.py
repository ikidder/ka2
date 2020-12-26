from flask import Blueprint, request, current_app, render_template, url_for, flash, request, abort, g
from flask_login import current_user, login_required
from flask_login.config import EXEMPT_METHODS
from functools import wraps
import time
import datetime
from ka import db
from ka.models import User, HttpEvent, EventAggregate

admin_app = Blueprint('admin', __name__)


def start_timer():
    g.start = time.time()


def log_request(response):
    """reference: https://dev.to/rhymes/logging-flask-requests-with-colors-and-structure--7g1
    """
    if request.path == '/favicon.ico':
        return response
    elif request.path.startswith('/static'):
        return response

    try:
        now = time.time()
        ellapsed_time = (now - g.start) * 1000
        datestamp = datetime.datetime.utcnow()
        user = current_user.id if current_user.is_authenticated else None
        method = request.method
        path = request.path
        query = request.query_string.decode('utf-8')
        if path[-1] == '?':
            path = path[:-1]
        status_code = response.status_code
        referrer = request.referrer
        requesting_addr = request.headers.get('X-Forwarded-For', request.remote_addr)
        responding_addr = request.host
        user_agent = request.user_agent.string

        event = HttpEvent(
            datestamp=datestamp,
            user=user,
            method=method,
            path=path,
            query=query,
            status_code=status_code,
            ellapsed_time=ellapsed_time,
            referrer=referrer,
            requesting_addr=requesting_addr,
            responding_addr = responding_addr,
            user_agent=user_agent
        )

        db.session.add(event)
        db.session.commit()
    except Exception as ex:
        print('*' * 10, 'Exception in event logging:')
        print(ex)
        print('*' * 10)

    return response


admin_app.before_app_request(start_timer)
admin_app.after_app_request(log_request)


def admin_required(func):
    """Checks if the user is an administrator.
    Based on login_required from flask_login.
    reference: https://github.com/maxcountryman/flask-login/blob/d7b5bcf5d003274227be5c19104c59a821097cd1/flask_login/utils.py
    """
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get('LOGIN_DISABLED'):
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.is_admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)
    return decorated_view


@admin_app.route("/admin/dashboard", methods=['GET'])
@login_required
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html', title='Dashboard')



