from flask import (render_template, url_for, flash,
                   redirect, request, abort, Blueprint)
from flask_login import current_user, login_required
from ka.database import Session, get_page
from ka.models import Score, Measure, to_ordinal_string, ForPlayers
from ka.scores.forms import ScoreForm, MeasureForm, DeleteMeasureForm, DeleteScoreForm
from datetime import datetime


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
            for_players=form.for_players.data,
            created=datetime.utcnow()
        )
        Session.add(score)
        Session.commit()
        flash('Your score has been created!', 'success')
        return redirect(url_for('scores.new_measure', score_path=score.id))
    return render_template('create_score.html', title='New Score',
                           form=form, legend='New Score')


@scores_app.route("/score/<string:score_path>/measure/new", methods=['GET', 'POST'])
@login_required
def new_measure(score_path):
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.composer != current_user:
        abort(403)
    form = MeasureForm()
    if form.validate_on_submit():
        measure = Measure(
            _name=form.name.data,
            tempo=form.tempo.data,
            dynamic=form.dynamic.data,
            text=form.text.data,
            duration=form.duration.data,
            created=datetime.utcnow(),
            _ordinal=max((x.ordinal for x in s.measures)) + 1 if s.measures else 0,
            score=s
        )
        Session.add(measure)
        Session.commit()
        flash('Your measure has been created!', 'success')
        return redirect(url_for('scores.new_measure', score_path=s.path))
    else:
        ordinal = max((x.ordinal for x in s.measures)) + 1 if s.measures else 0
        title = to_ordinal_string(ordinal) + ' Measure'
        form.name.data = title
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
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.composer != current_user:
        abort(403)

    measures = s.measures

    above_this_measure = Session.query(Measure).filter_by(path=measure_path).first()
    if not above_this_measure:
        abort(404)
    if above_this_measure.score.id != s.id:
        abort(404)
    index = measures.index(above_this_measure)

    measure = Measure()
    form = MeasureForm()
    if form.validate_on_submit():
        measure = Measure(
            _name=form.name.data,
            tempo=form.tempo.data,
            dynamic=form.dynamic.data,
            text=form.text.data,
            duration=form.duration.data,
            created=datetime.utcnow(),
            _ordinal=above_this_measure.ordinal,
            score=s
        )

        measures = measures[:index] + [measure] + measures[index:]
        for i, m in enumerate(measures):
            m.ordinal = i
        Session.add(s)
        Session.commit()
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
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    title = s.name + ' by ' + s.composer.name
    return render_template('score.html', title=title, score=s, measures=s.measures)


@scores_app.route("/score/<string:score_path>/measure/<string:measure_path>")
@login_required
def measure(score_path, measure_path):
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    matches = list(filter(lambda x: x.path == measure_path, s.measures))
    if not matches:
        abort(404)
    m = matches[0]

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
    return render_template('measure.html', title=title, score=s, measure=m, prev_measure=prev_measure, next_measure=next_measure)


@scores_app.route("/score/<string:score_path>/update", methods=['GET', 'POST'])
@login_required
def update_score(score_path):
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.composer != current_user:
        abort(403)
    form = ScoreForm()
    if form.validate_on_submit():
        s.name = form.name.data
        s.text = form.text.data
        s.for_players = form.for_players.data
        Session.commit()
        flash('Your score has been updated!', 'success')
        if s.measures:
            return redirect(url_for('scores.update_measure', score_path=s.path, measure_path=s.measures[0].path))
        else:
            return redirect(url_for('scores.new_measure', score_path=s.path))
    elif request.method == 'GET':
        form.title.data = s.name
        form.description.data = s.text
        form.for_players.data = s.for_players.value
    return render_template('create_score.html', title='Edit Score',
                           form=form, legend='Edit Score')


@scores_app.route("/score/<string:score_path>/measure/<string:measure_path>/update", methods=['GET', 'POST'])
@login_required
def update_measure(score_path, measure_path):
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    m = Session.query(Measure).filter_by(path=measure_path).first()
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
        Session.commit()
        flash('Your measure has been updated!', 'success')
        if next_measure:
            return redirect(url_for(
                'scores.update_measure',
                score_path=next_measure.score.id,
                measure_id=next_measure.id,
                _anchor='editing'
            ))
        else:
            return redirect(url_for('scores.new_measure', score_path=s.path, _anchor='editing'))
    elif request.method == 'GET':
        form.title.data = m.title
        form.tempo.data = m.tempo
        form.dynamic.data = m.dynamic
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


@scores_app.route("/score/<int:score_path>/delete", methods=['GET','POST'])
@login_required
def delete_score(score_path):
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.user_id != current_user.id:
        abort(403)

    form = DeleteScoreForm()
    if form.validate_on_submit():
        for m in s.measures:
            Session.delete(m)
        Session.delete(s)
        Session.commit()
        flash('Your score has been deleted!', 'success')
        return redirect(url_for('main.index'))

    return render_template('delete_score.html', title='Delete Score', form=form, score=s)



@scores_app.route("/score/<int:score_path>/measure/<int:measure_id>/delete", methods=['GET','POST'])
@login_required
def delete_measure(score_path, measure_id):
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    if s.user_id != current_user.id:
        abort(403)
    m = Session.query(Measure).get(measure_id)
    if not m:
        abort(404)
    if s.id != m.score.id:
        abort(404)

    form = DeleteMeasureForm()
    if form.validate_on_submit():
        Session.delete(m)
        Session.commit()
        flash('Your measure has been deleted!', 'success')
        return redirect(url_for('scores.score', score_path=score.path))

    return render_template('delete_measure.html', title='Delete Measure', form=form, score=s, measure=m)


@scores_app.route('/scores', methods=['GET'])
@login_required
def scores():
    page = request.args.get('page', 1, type=int)
    page_result = get_page(Session.query(Score).order_by(Score.created.desc()), page)
    return render_template(
        'scores.html',
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
    page_result = get_page(Session.query(Score).filter_by(for_players=fp).order_by(Score.created.desc()), page)
    return render_template('scores.html', result=page_result)


@scores_app.route("/score/<string:score_path>/copy", methods=['GET', 'POST'])
@login_required
def copy_score(score_path):
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)

    copy = Score()
    copy.name = make_copy_title(s)
    copy.composer = current_user
    copy.text = f'Variation on the score \n [{s.title}]({url_for("scores.score", score_path=s.path)}) \nby [{s.composer.name}]({url_for("users.user_scores", username=s.composer.name)}) \n\n' + s.description
    copy.for_players = s.for_players

    for m in s.measures:
        copy_m = Measure()
        copy_m.name = m.name
        copy_m.tempo = m.tempo
        copy_m.dynamic = m.dynamic
        copy_m.text = m.text
        copy_m.duration = m.duration
        copy_m.ordinal = m.ordinal
        copy.measures.append(copy_m)

    Session.add(copy)
    Session.commit()

    return redirect(url_for('scores.score', score_path=copy.path))


# helper function
def make_copy_title(s):
    i = 1
    while True:
        title = f'{to_ordinal_string(i)} Variation on {s.title}'
        existing_title = Session.query(Score).filter_by(title=title).first()
        if not existing_title:
            return title
        i = i + 1


@scores_app.route("/score/<string:score_path>/ending")
@login_required
def ending(score_path):
    s = Session.query(Score).filter_by(path=score_path).first()
    if not s:
        abort(404)
    title = 'End of ' + s.title + ' by ' + s.composer.name
    return render_template('ending.html', title=title, score=s, measures=s.measures)