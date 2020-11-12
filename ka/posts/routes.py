from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from ka.database import get_page
from ka import Session
from ka.models import Post
from ka.posts.forms import PostForm, DeletePostForm


posts_app = Blueprint('posts', __name__)


@posts_app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(name=form.name.data, text=form.text.data, composer=current_user)
        Session.add(post)
        Session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('posts.posts'))
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')


@posts_app.route("/post/<string:post_path>")
@login_required
def post(post_path):
    p = Session.query(Post).filter_by(path=post_path).first()
    if not p:
        abort(404)
    return render_template('post.html', title=p.name, post=p)


@posts_app.route("/post/<string:post_path>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_path):
    p = Session.query(Post).filter_by(path=post_path).first()
    if not p:
        abort(404)
    if p.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        p.title = form.title.data
        p.text = form.text.data
        Session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=p.id))
    elif request.method == 'GET':
        form.name.data = p.title
        form.text.data = p.content
    return render_template('create_post.html', title='Edit Post',
                           form=form, legend='Edit Post')


@posts_app.route("/post/<string:post_path>/delete", methods=['GET','POST'])
@login_required
def delete_post(post_path):
    p = Session.query(Post).filter_by(path=post_path).first()
    if not p:
        abort(404)
    if p.user_id != current_user.id:
        abort(403)

    form = DeletePostForm()
    if form.validate_on_submit():
        Session.delete(p)
        Session.commit()
        flash('Your post has been deleted!', 'success')
        return redirect(url_for('posts.posts'))

    return render_template('delete_post.html', title='Delete Post', form=form, post=p)


@posts_app.route('/posts', methods=['GET'])
@login_required
def posts():
    page = request.args.get('page', 1, type=int)
    page_result = get_page(Session.query(Post).order_by(Post.created.desc()), page)
    return render_template('posts.html', result=page_result)
