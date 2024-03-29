from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from ka.database import get_page
from ka import db
from ka.models import Score, Measure, to_ordinal_string, ForPlayers, Visibility, User, Tag, Feature, tempo_alt_text, dynamic_alt_text
from ka.scores.forms import ScoreForm, MeasureForm, DeleteMeasureForm, DeleteScoreForm
from datetime import datetime
from sqlalchemy import or_, and_, case, nullslast, func, desc, text


scores_app = Blueprint('scores', __name__)


@scores_app.route("/score/new", methods=['GET', 'POST'])
@login_required
def new_score():
    form = ScoreForm()
    if form.validate_on_submit():
        score = Score(
            name=form.name.data,
            composer=current_user,
            text=form.text.data,
            measures=[],
            count_plays=0,
            count_favorites=0,
            for_players=ForPlayers[form.for_players.data],
            created=datetime.utcnow()
        )
        score.tags = Tag.extract_tags(score.text)
        score.composer.count_scores = score.composer.count_scores + 1
        db.session.add(score)
        db.session.commit()
        flash('Your score has been created!', 'success')
        return redirect(url_for('scores.new_measure', score_path=score.path))
    form = ScoreForm(for_players='TwoAny')  # otherwise will default to 'one man'
    return render_template('create_score.html', title='New Score',
                           form=form, legend='New Score')


@scores_app.route("/score/<string:score_path>/measure/new", methods=['GET', 'POST'])
@login_required
def new_measure(score_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.composer != current_user:
        abort(403)
    form = MeasureForm()
    if form.validate_on_submit():
        m = Measure(
            _name=form.name.data,
            tempo=form.tempo.data,
            dynamic=form.dynamic.data,
            text=form.text.data,
            duration=form.duration.data,
            created=datetime.utcnow(),
            _ordinal=max((x.ordinal for x in s.measures)) + 1 if s.measures else 0,
            score=s
        )
        db.session.add(m)
        db.session.add(s)
        db.session.commit()
        flash('Your measure has been created!', 'success')
        return redirect(url_for('scores.new_measure', score_path=s.path))
    else:
        ordinal = max((x.ordinal for x in s.measures)) + 1 if s.measures else 0
        name = to_ordinal_string(ordinal) + ' Measure'
        form.name.data = name
        if s.measures:
            prev_measure = s.measures[-1]
            form.duration.data = prev_measure.duration
            form.tempo.data = prev_measure.tempo.value
            form.dynamic.data = prev_measure.dynamic.value
    return render_template('create_measure.html',
                           title='New Measure',
                           form=form,
                           legend='New Measure',
                           score=s,
                           measures=s.measures,
                           append=True)


@scores_app.route("/score/<string:score_path>/measure/<string:measure_path>/new-measure-before", methods=['GET', 'POST'])
@login_required
def new_measure_before(score_path, measure_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.composer != current_user:
        abort(403)

    above_this_measure = Measure.query.filter_by(path=measure_path).first()
    if not above_this_measure:
        abort(404)
    if above_this_measure.score.id != s.id:
        abort(404)

    index = above_this_measure.ordinal

    measure = Measure()
    form = MeasureForm()
    if form.validate_on_submit():
        measure = Measure(
            _name=form.name.data,
            tempo=form.tempo.data,
            dynamic=form.dynamic.data,
            text=form.text.data,
            duration=form.duration.data,
            created=datetime.utcnow()
        )

        s.measures = s.measures[:index] + [measure] + s.measures[index:]
        for i, m in enumerate(s.measures):
            m.ordinal = i
        db.session.add(s)
        db.session.commit()
        flash('Your measure has been created!', 'success')
        return redirect(url_for('scores.score', score_path=s.path))
    else:
        measure.id = -1
        measures = list(s.measures)[:index] + [measure] + list(s.measures)[index:]

    return render_template('create_measure.html',
                           title='New Measure',
                           form=form,
                           legend='New Measure',
                           score=s,
                           measures=measures,
                           current_measure=measure,
                           append=False)


@scores_app.route("/score/<string:score_path>/measure/<string:measure_path>/new-measure-after", methods=['GET', 'POST'])
@login_required
def new_measure_after(score_path, measure_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.composer != current_user:
        abort(403)

    below_this_measure = Measure.query.filter_by(path=measure_path).first()
    if not below_this_measure:
        abort(404)
    if below_this_measure.score.id != s.id:
        abort(404)

    index = below_this_measure.ordinal + 1

    measure = Measure()
    form = MeasureForm()
    if form.validate_on_submit():
        measure = Measure(
            _name=form.name.data,
            tempo=form.tempo.data,
            dynamic=form.dynamic.data,
            text=form.text.data,
            duration=form.duration.data,
            created=datetime.utcnow()
        )
        s.measures = s.measures[:index] + [measure] + s.measures[index:]
        for i, m in enumerate(s.measures):
            m.ordinal = i
        db.session.add(s)
        db.session.commit()
        flash('Your measure has been created!', 'success')
        return redirect(url_for('scores.score', score_path=s.path))
    else:
        measure.id = -1
        measures = list(s.measures)[:index] + [measure] + list(s.measures)[index:]

    return render_template('create_measure.html',
                           title='New Measure',
                           form=form,
                           legend='New Measure',
                           score=s,
                           measures=measures,
                           current_measure=measure,
                           append=False)


@scores_app.route("/score/<string:score_path>")
@login_required
def score(score_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.visibility == Visibility.HIDDEN:
        abort(404)
    variation = None
    if s.variation_on_id:
        variation = Score.query.get(s.variation_on_id)
    title = s.name + ' by ' + s.composer.name
    return render_template('score.html', title=title, score=s, variation=variation, measures=s.measures)


@scores_app.route("/score/<string:score_path>/variations")
@login_required
def score_variations(score_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.visibility == Visibility.HIDDEN:
        abort(404)
    page = request.args.get('page', 1, type=int)
    page_result = get_page(
        Score.query
            .filter(Score.visibility == Visibility.PUBLIC)
            .filter(Score.variation_on_id == s.id)
            .order_by(desc(text("count_plays + count_favorites")), Score.created.desc()),
        page
    )
    title = 'Variations on ' + s.name + ' by ' + s.composer.name
    return render_template(
        'scores.html',
        title=title,
        filtered_on=s,
        result=page_result
    )


@scores_app.route("/score/<string:score_path>/measure/<string:measure_path>")
@login_required
def measure(score_path, measure_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    matches = list(filter(lambda x: x.path == measure_path, s.measures))
    if not matches:
        abort(404)
    m = matches[0]

    if s.visibility == Visibility.HIDDEN:
        abort(404)

    prev_ord = m.ordinal - 1
    matches = list(filter(lambda x: x.ordinal == prev_ord, s.measures))
    prev_measure = None
    if matches:
        prev_measure = matches[0]

    next_ord = m.ordinal + 1
    matches = list(filter(lambda x: x.ordinal == next_ord, s.measures))
    next_measure = None
    if matches:
        next_measure = matches[0]

    title = m.name + ' from ' + m.score.name
    return render_template(
        'measure.html',
        title=title,
        score=s,
        measure=m,
        prev_measure=prev_measure,
        next_measure=next_measure,
        show_controls=True
    )


@scores_app.route("/score/<string:score_path>/update", methods=['GET', 'POST'])
@login_required
def update_score(score_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.composer != current_user:
        abort(403)
    form = ScoreForm()
    if form.validate_on_submit():
        s.name = form.name.data
        s.text = form.text.data
        s.for_players = form.for_players.data
        s.tags = Tag.extract_tags(s.text)
        db.session.commit()
        flash('Your score has been updated!', 'success')
        if s.measures:
            return redirect(url_for('scores.update_measure', score_path=s.path, measure_path=s.measures[0].path))
        else:
            return redirect(url_for('scores.new_measure', score_path=s.path))
    elif request.method == 'GET':
        form.name.data = s.name
        form.text.data = s.text
        form.for_players.data = s.for_players.name
    return render_template('create_score.html', title='Edit Score',
                           form=form, legend='Edit Score')


@scores_app.route("/score/<string:score_path>/measure/<string:measure_path>/update", methods=['GET', 'POST'])
@login_required
def update_measure(score_path, measure_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    m = Measure.query.filter_by(path=measure_path).first()
    if not m:
        abort(404)
    if s.id != m.score.id:
        abort(404)
    if m.score.composer != current_user:
        abort(403)

    next_ord = m.ordinal + 1
    matches = list(filter(lambda x: x.ordinal == next_ord, s.measures))
    next_measure = None
    if matches:
        next_measure = matches[0]

    form = MeasureForm()
    if form.validate_on_submit():
        m.name = form.name.data
        m.tempo = form.tempo.data
        m.dynamic = form.dynamic.data
        m.text = form.text.data
        m.duration = form.duration.data
        s._set_duration()
        db.session.commit()
        flash('Your measure has been updated!', 'success')
        if next_measure:
            return redirect(url_for(
                'scores.update_measure',
                score_path=next_measure.score.path,
                measure_path=next_measure.path,
                _anchor='editing'
            ))
        else:
            return redirect(url_for('scores.new_measure', score_path=s.path, _anchor='editing'))
    elif request.method == 'GET':
        form.name.data = m.name
        form.tempo.data = m.tempo.name
        form.dynamic.data = m.dynamic.name
        form.text.data = m.text
        form.duration.data = m.duration
    return render_template('create_measure.html',
                           title='Edit Measure',
                           form=form,
                           legend='Edit Measure',
                           score=s,
                           measures=s.measures,
                           current_measure=m,
                           append=False)


@scores_app.route("/score/<string:score_path>/delete", methods=['GET','POST'])
@login_required
def delete_score(score_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.user_id != current_user.id:
        abort(403)

    form = DeleteScoreForm()
    if form.validate_on_submit():
        s.composer.count_scores = s.composer.count_scores - 1
        for m in s.measures:
            db.session.delete(m)
        db.session.delete(s)
        db.session.commit()
        flash('Your score has been deleted!', 'success')
        return redirect(url_for('main.index'))

    return render_template('delete_score.html', title='Delete Score', form=form, score=s)



@scores_app.route("/score/<string:score_path>/measure/<string:measure_path>/delete", methods=['GET','POST'])
@login_required
def delete_measure(score_path, measure_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.user_id != current_user.id:
        abort(403)
    m = Measure.query.filter_by(path=measure_path).first()
    if not m:
        abort(404)
    if s.id != m.score.id:
        abort(404)

    form = DeleteMeasureForm()
    if form.validate_on_submit():
        db.session.delete(m)
        db.session.commit()
        db.session.add(s)
        s._set_duration()
        for i, m in enumerate(s.measures):
            m.ordinal = i
        db.session.commit()
        flash('Your measure has been deleted!', 'success')
        return redirect(url_for('scores.score', score_path=s.path))

    return render_template('delete_measure.html', title='Delete Measure', form=form, score=s, measure=m)


@scores_app.route('/scores', methods=['GET'])
@login_required
def scores():
    page = request.args.get('page', 1, type=int)

    # case([(Feature.pinned == True, 1)], else_ = 0)
    page_result = get_page(
        Score.query
            .join(Feature, (Score.id == Feature.content_id), isouter=True)
            .filter(Score.visibility == Visibility.PUBLIC)
            .order_by(
                nullslast(Feature.pinned.desc()),
                nullslast(Feature.created.desc()),
                Score.created.desc(),
            ),
        page
    )
    return render_template(
        'scores.html',
        title='Scores',
        result=page_result
    )


@scores_app.route('/scores/<string:for_whom>', methods=['GET'])
@login_required
def scores_for_players(for_whom):
    page = request.args.get('page', 1, type=int)
    param = for_whom.replace('-', ' ')
    try:
        fp = ForPlayers(param)
    except:
        abort(404)
    page_result = get_page(
        Score.query
            .join(Feature, (Score.id == Feature.content_id), isouter=True)
            .filter(Score.visibility == Visibility.PUBLIC)
            .filter(Score.for_players == fp)
            .order_by(
            nullslast(Feature.pinned.desc()),
            nullslast(Feature.created.desc()),
            Score.created.desc(),
        ),
        page
    )
    return render_template(
        'scores.html',
        title='Scores ' + fp.value,
        filtered_on=fp,
        result=page_result
    )


@scores_app.route("/user/<string:user_path>/scores")
@login_required
def user_scores(user_path):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(path=user_path).first()
    if not user:
        abort(404)
    page_result = get_page(
        Score.query
            .filter(Score.user_id == user.id)
            .filter(or_(Score.visibility == Visibility.PUBLIC, Score.visibility == Visibility.PRIVATE))
            .order_by(Score.count_favorites.desc(), Score.created.desc()),
        page
    )
    return render_template(
        'user_scores.html',
        title='Scores by ' + user.name,
        filtered_on=user,
        result=page_result
    )


@scores_app.route("/score/<string:score_path>/copy", methods=['GET', 'POST'])
@login_required
def copy_score(score_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)

    copy = Score()
    copy.name = make_copy_title(s)
    copy.composer = current_user
    copy.text = s.text
    copy.for_players = s.for_players
    copy.variation_on_id = s.id

    for m in s.measures:
        copy_m = Measure()
        copy_m.name = m.name
        copy_m.tempo = m.tempo
        copy_m.dynamic = m.dynamic
        copy_m.text = m.text
        copy_m.duration = m.duration
        copy_m.ordinal = m.ordinal
        copy.measures.append(copy_m)

    current_user.count_scores = current_user.count_scores + 1
    db.session.add(copy)
    db.session.commit()

    flash("You've created a variation! You can now edit the score to make it your own.", 'success')
    return redirect(url_for('scores.score', score_path=copy.path))


# helper function
def make_copy_title(s):
    i = 1
    while True:
        name = f'{to_ordinal_string(i)} Variation on {s.name}'
        existing_name = Score.query \
            .filter(and_(Score.name == name, Score.user_id == current_user.id)) \
            .first()
        if not existing_name:
            return name
        i = i + 1


@scores_app.route("/score/<string:score_path>/ending")
@login_required
def ending(score_path):
    s = Score.query.filter_by(path=score_path).first()
    if not s:
        abort(404)
    title = 'End of ' + s.name + ' by ' + s.composer.name
    return render_template('ending.html', title=title, score=s, measures=s.measures)



# *************************************************
#  Template Tests
# *************************************************


@scores_app.app_template_test("User")
def is_user(obj):
    return isinstance(obj, User)

@scores_app.app_template_test("ForPlayers")
def is_for_players(obj):
    return isinstance(obj, ForPlayers)

@scores_app.app_template_test("Score")
def is_score(obj):
    return isinstance(obj, Score)


# *************************************************
#  Template Filters
# *************************************************

def tempo_description(t):
    return tempo_alt_text[t]

scores_app.add_app_template_filter(tempo_description)

def dynamic_description(d):
    return dynamic_alt_text[d]

scores_app.add_app_template_filter(dynamic_description)
