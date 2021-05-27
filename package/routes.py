from flask import render_template, flash, request, abort, redirect, url_for, send_from_directory
from flask_cors import cross_origin
from package import app, db
from package.forms import Lesson
from package.getResults import getResultsRaw
from package.models import Calculation, User, BuffRates
import datetime, json, re, os
from package.utils import *



@app.before_request
def handleUser():
    user_ip = getUserIP(request)

    if not User.query.filter_by(ip=user_ip).first():
        user = User(ip=user_ip)
        db.session.add(user)
        db.session.commit()
    user = User.query.filter_by(ip=user_ip).first()
    user.latest_visit = datetime.datetime.now()
    db.session.commit()


@app.route("/", methods=['GET', 'POST'])
def home():
    user_ip = getUserIP(request)

    form = Lesson()
    if request.method == "POST":
        if form.validate_on_submit():
            results = getResultsRaw(form.content.data)

            calc = Calculation(results=results, ip=user_ip, raw=form.content.data)
            db.session.add(calc)
            db.session.commit()

            return redirect(url_for('results'))
        flash(form.errors['content'], 'danger')

    return render_template('home.html', form=form, isinstance=isinstance, type=type)

@app.route("/results")
def results():
    user_ip = getUserIP(request)
    submitLocationToDatabase(user_ip, "/results")
    user = User.query.get(user_ip)

    if not user:
        flash('Du er ikke registreret - prøv igen', 'info')
        return redirect(url_for('home'))
    if not user.Calculations:
        flash('Du har ikke modtaget nogle resultater endnu...', 'info')
        return redirect(url_for('home'))

    page = request.args.get('Calculation', 1, type=int)
    resultsInfo = Calculation.query.filter_by(ip=user_ip).order_by(Calculation.time.desc()).paginate(page=page, per_page=1)

    return render_template('results.html', title='Results', resultsInfo=resultsInfo, json=json, enumerate=enumerate, current_time=datetime.datetime.now())

@app.route("/dashboard")
def admin():
    user_ip = getUserIP(request)
    submitLocationToDatabase(user_ip, "/dashboard")

    if user_ip == os.environ.get("OWNER_IP", default="") or user_ip == "127.0.0.1":
        users = User.query.order_by(User.first_visit.desc()).filter(User.latest_url_visited != "/")
        return render_template('dashboard.html', users=users, calc_count=Calculation.query.count(), json=json, User=User, now=datetime.datetime.now())
    return redirect(url_for('home'))
    
@app.route('/robots.txt')
def robots():
    return send_from_directory(app.static_folder, request.path[1:])
    
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
# This is just for the Chrome extension, I'm r***ded so this is not secured properly pls no abuse

@app.route("/api/", methods=['POST'])
def api():
    user_ip = getUserIP(request)
    submitLocationToDatabase(user_ip, "/api")

    code = request.data.decode('utf-8')
    
    locs = [i.start() for i in re.finditer('"explanation":"', code)]
    if not locs:
        return {
                'status_code' : 0,
                'message' : 'Ingen spørgsmål blev fundet'
            }

    codeCalced = getResultsRaw(code)

    calc = Calculation(results=codeCalced, ip=user_ip, raw=code)
    db.session.add(calc)
    db.session.commit()

    success = {
        'status_code' : 1,
        'message' : "Success!"
    }
    return success


# Buff
# This is completely irrelevant to Einsteinfessor, I'm just merging projects

@app.route('/buffcurrency')
@cross_origin()
def buff():
		return json.loads(BuffRates.query.first().rates)
