from flask import render_template, flash, request, abort, redirect, url_for
from package import app, db
from package.forms import Lesson
from package.getResults import getResultsRaw
from package.models import Calcuation, User
import datetime, package.admin, requests, json, re, os

prod = app.config['ENV'] == 'prod'

@app.before_request
def handleUser():
    user_ip = request.header['X-Forwarded-For'] if prod else request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    print(user_ip)
    if not User.query.filter_by(ip=user_ip).first():
        user = User(ip=user_ip)
        db.session.add(user)
        db.session.commit()
    user = User.query.filter_by(ip=user_ip).first()
    user.latest_visit = datetime.datetime.now()
    db.session.commit()


@app.route("/", methods=['GET', 'POST'])
def home():
    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    form = Lesson()
    if request.method == "POST":
        if form.validate_on_submit():
            results = getResultsRaw(form.content.data)

            calc = Calcuation(results=results, ip=user_ip, raw=form.content.data)
            db.session.add(calc)
            db.session.commit()

            return redirect(url_for('results'))
        flash(form.errors['content'], 'danger')

    return render_template('home.html', form=form, isinstance=isinstance, type=type)

@app.route("/results")
def results():
    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user = User.query.get(user_ip)
    user.latest_url_visited = "/results"
    db.session.commit()

    if not user:
        flash('Du er ikke registreret - prøv igen', 'info')
        return redirect(url_for('home'))
    if not user.calcuations:
        flash('Du har ikke modtaget nogle resultater endnu...', 'info')
        return redirect(url_for('home'))

    page = request.args.get('calcuation', 1, type=int)
    resultsInfo = Calcuation.query.filter_by(ip=user_ip).order_by(Calcuation.time.desc()).paginate(page=page, per_page=1)

    return render_template('results.html', title='Results', resultsInfo=resultsInfo, json=json, enumerate=enumerate, current_time=datetime.datetime.now())

@app.route("/dashboard")
def admin():
    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user = User.query.filter_by(ip=user_ip).first()
    user.latest_url_visited = "/dashboard"
    print(user)
    db.session.commit()
    if user_ip == "5.186.54.197" or user_ip == "127.0.0.1":
        #package.admin.IP() #doesn't work currently
        users = User.query.order_by(User.first_visit.desc())
        page = request.args.get('page', 1, type=int)
        return render_template('dashboard.html', users=users, calc_count=Calcuation.query.count(), json=json, page=page, User=User)
    return redirect(url_for('home'))
    

@app.errorhandler(404)
def notfound(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

@app.errorhandler(405)
def methodnotallowed(e):
    return render_template('errors/405.html'), 405

@app.errorhandler(500)
def servererror(e):
    return render_template('errors/500.html'), 500


# API

@app.route("/api/", methods=['POST'])
def api():
    user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user = User.query.filter_by(ip=user_ip).first()
    user.latest_url_visited = "/api"
    db.session.commit()

    code = request.data.decode('utf-8')
    
    locs = [i.start() for i in re.finditer('"explanation":"', code)]
    if not locs:
        return {
                'status_code' : 0,
                'message' : 'Ingen spørgsmål blev fundet'
            }

    codeCalced = getResultsRaw(code)

    calc = Calcuation(results=codeCalced, ip=user_ip, raw=code)
    db.session.add(calc)
    db.session.commit()

    success = {
        'status_code' : 1,
        'message' : "Success!",
        'results' : codeCalced
    } # For the Flutter app, additional information is included. The Chrome extension
    # should just ignore this.
    return success
