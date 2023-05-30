#!/usr/bin/env python3

# Base packages
import os
import sys
import uuid
import tempfile
import evaluator
import traceback
import subprocess as sp

# Local packages required before flask
from setup import *
import db
import lgnman

# Flask and friends
from flask import Flask, redirect, request, session, \
                  render_template, url_for
from flask_login import login_required, current_user
import flask
import flask_login
import werkzeug as wz

# Create app
app = Flask(__name__)
# Secure app
set_secret_key(app)
# Setup database
db.setup(app)
# Setup login manager
lgnman.setup(app)


# with app.app_context():
    # print(db.Group.query.all())

def execute(exefile, args=[]):
    eargs = [exefile]
    eargs.extend([str(a) for a in args])
    proc = sp.Popen(eargs, stdout=sp.PIPE, stderr=sp.PIPE)
    out, err = proc.communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8")
    return out, err, proc
# end def



@app.route('/')
def root():
    if not current_user.is_authenticated:
        return render_template("index.html", groups=db.fetch_groups_we())
    return render_template("index.html", groups=db.fetch_groups())
#end def



@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='img/braces.ico'))
#end def



@app.route('/admin')
# @login_required
def admin():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    e = db.fetch_evaluators(current_user.tid)
    return render_template('admin/index.html', evaluators=e)
#end def



@app.route('/admin/evaluator/new', methods = ['POST', 'GET'])
# @login_required
def evaluator_new():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if request.method != 'POST':
        g = db.fetch_groups(current_user.tid)
        return render_template("admin/specform.html", groups=g)
        return redirect("/", code=302)

    required = [ 'name', 'group', 'enabled' ]
    for r in required:
        if r not in request.form:
            return flask.abort(400)
    if len(request.files) < 1 or 'specfile' not in request.files:
        return flask.abort(400)

    f = request.files['specfile']
    fname = make_random_name('.xml')
    fpath = os.path.join(SPECSF_FOLDER, fname)
    f.save(fpath)

    e = db.Evaluator(
        name=request.form['name'],
        groupId=int(request.form['group']),
        file=fname,
        active=str2bool(request.form['enabled']))
    db.get_db().session.add(e)
    db.get_db().session.commit()

    return redirect(url_for('admin'))
    # return render_template("admin/specform.html")
#end def



@app.route('/admin/evaluator/<int:eid>/delete')
@login_required
def evaluator_delete(eid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    e = db.fetch_evaluator(eid)
    if e:
        delete(e.file)
        db.get_db().session.delete(e)
        db.get_db().session.commit()
    return redirect(url_for('admin'))
#end def



@app.route('/admin/evaluator/<int:eid>/download')
@login_required
def evaluator_download(eid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    e = db.fetch_evaluator(eid)
    if e:
        path = os.path.join(SPECSF_FOLDER, e.file)
        response = ''
        with open(path, 'r') as f:
            response = flask.make_response(f.read())
        response.headers.set('Content-Type', 'application/xml')
        response.headers.set('Content-Disposition', 'attachment', filename=e.file)
        return response
        # This one below is good for binary files only
        # import io
        # with open(path, 'rb') as f:
        #     return flask.send_file(
        #         io.BytesIO(f.read()),
        #         mimetype='application/xml',
        #         download_name=e.file
        #     )

    return redirect(url_for('admin'))
#end def



@app.route('/admin/evaluator/<int:eid>/toggle')
@login_required
def evaluator_toggle_active(eid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    e = db.fetch_evaluator(eid)
    if e:
        e.active = not e.active;
        db.get_db().session.commit()
    return redirect(url_for('admin'))
#end def



@app.route('/admin/evaluator/<int:eid>', methods = ['POST', 'GET'])
@app.route('/admin/evaluator/<int:eid>/edit', methods = ['POST', 'GET'])
# @login_required
def evaluator_edit(eid):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    e = db.fetch_evaluator(eid)
    if not e:
        return redirect(url_for('admin'))

    if request.method != 'POST':
        g = db.fetch_groups(current_user.tid)
        return render_template("admin/specform.html", evaluator=e, groups=g)

    required = [ 'name', 'group', 'enabled' ]
    for r in required:
        if r not in request.form:
            return flask.abort(400)

    if 'specfile' in request.files:
        f = request.files['specfile']
        fname = make_random_name('.xml')
        fpath = os.path.join(SPECSF_FOLDER, fname)
        f.save(fpath)
        delete(e.file)
        e.file = fname

    e.name = request.form['name']
    e.groupId = int(request.form['group'])
    e.active = str2bool(request.form['enabled'])
    db.get_db().session.commit()

    return redirect(url_for('admin'))
#end def



@app.route('/admin/group/new', methods = ['POST', 'GET'])
# @login_required
def group_new():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    if request.method != 'POST':
        return render_template("admin/group.html")

    required = [ 'gsubject', 'gnum' ]
    for r in required:
        if r not in request.form:
            return flask.abort(400)

    g = db.Group(
        teacherId=current_user.tid,
        subject=request.form['gsubject'],
        number=int(request.form['gnum'])
    )
    db.get_db().session.add(g)
    db.get_db().session.commit()

    return redirect(url_for('admin'))
#end def



@app.route('/admin/group/<int:group_id>', methods = ['POST', 'GET'])
@app.route('/admin/group/<int:group_id>/edit', methods = ['POST', 'GET'])
# @login_required
def group_edit(group_id):
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    g = db.fetch_group(group_id)
    if not g:
        return redirect(url_for('admin'))

    if request.method != 'POST':
        return render_template("admin/group.html", group=g)

    required = [ 'gsubject', 'gnum' ]
    for r in required:
        if r not in request.form:
            return flask.abort(400)

    g.subject=request.form['gsubject']
    g.number=int(request.form['gnum'])
    db.get_db().session.commit()

    return redirect(url_for('admin'))
#end def



@app.route('/group/<int:group_id>')
def upload_code(group_id):
    g = db.fetch_group(group_id)
    try:
        return render_template("form.html", group=g)
    except:
        return render_template("error.html", traceback=traceback.format_exc())
#end def



@app.route('/eval', methods = ['POST', 'GET'])
def eval():
    if request.method != 'POST':
        return redirect("/", code=302)
    try:
        sr = ''
        path = ''
        if not 'evaluator' in request.form:
            return redirect("/", code=302)
        sr = 'Evaluator: {}\n'.format(request.form['evaluator'])
        evaluator = db.fetch_evaluator(request.form['evaluator'])
        if not evaluator:
            return redirect("/", code=302)
        specs = evaluator.file
        sr = 'Evaluator: {}\n'.format(evaluator.name)
        if len(request.files) > 0 and 'codefile' in request.files:
            f = request.files['codefile']
            path = os.path.join(UPLOAD_FOLDER, wz.utils.secure_filename(f.filename))
            f.save(path)
            sr+= f'Uploaded file {f.filename}\n'
        elif not 'codetext' in request.form:
            return redirect("/", code=302)
        else:
            path = dumptemp(request.form['codetext'])
            path = fix_src_extension(evaluator.file, path)
            sr+= f'Created sourcecode file: {path}\n'

        report = evaluate(specs, path)
        delete(path)

        if isinstance(report, str) and os.path.isfile(report):
            uri = url_for('static', filename='reports/' + os.path.basename(report))
            return render_template("report.html", reporturi=uri)
        else:
            sr+= f'{report}\n' if report else 'Failed to evaluate uploaded code'
            g = db.fetch_group(evaluator.groupId)
            return render_template("form.html", group=g, results=sr)
    except:
        return render_template("error.html", traceback=traceback.format_exc())
#end def



@app.route('/login', methods=['GET', 'POST'])
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('admin/login.html')
    if 'username' not in request.form or 'password' not in request.form:
        return flask.abort(400)

    user = lgnman.login(request.form['username'], request.form['password'])
    if not user.is_authenticated:
        return render_template('admin/login.html', lgnerr=True)

    next = flask.request.args.get('next')
    # is_safe_url should check if the url is safe for redirects.
    # See http://flask.pocoo.org/snippets/62/ for an example.
    if not lgnman.is_safe_url(next):
        return flask.abort(400)

    return redirect(next or url_for('admin'))
#end def



@app.route('/logout', methods=['GET', 'POST'])
@app.route('/admin/logout', methods=['GET', 'POST'])
# @login_required
def logout():
    flask_login.logout_user()
    return redirect('/')



@app.route('/test')
def test():
    try:
        o, e, p = execute("gcc", ["--version"])
        return render_template(
            "test.html",
            pyver=sys.version,
            stdout=o,
            stderr=e,
            retcode=p.returncode
        )
    except:
        return render_template("error.html", traceback=traceback.format_exc())
#end def



def dumptemp(data):
    fd, path = tempfile.mkstemp(prefix='progeval_', suffix='', dir=UPLOAD_FOLDER)
    with open(path, 'w') as f:
        f.write(data)
    os.close(fd)
    return path
#end def



def evaluate(specs, source):
    begin_clean_old_reports()
    specs = os.path.join(SPECSF_FOLDER, specs)
    if not os.path.isfile(specs):
        return 'Evaluator not found'
        # return None
    ofname = uuid.uuid4().hex
    ofname = os.path.join(REPORT_FOLDER, f'{ofname}.pdf')
    # os.chdir(os.path.dirname(__file__))

    args = [ '-m', 'evaluator', specs, source, '--output', ofname]
    o, e, p = execute('python3', args)
    if p.returncode != 0:
        # cwd = os.getcwd()
        return 'Failed to execute evaluator\n' #+\
            # f'python3 ' + '\n  '.join(args) + \
            # f'\ncwd: {os.getcwd()}\ncout: {o}\ncerr: {e}'
        return None
    if not os.path.isfile(ofname):
        return 'Evaluator generated no file'
        # return None
    return ofname
#end def



def fix_src_extension(specs, srcpath):
    if not isinstance(srcpath, str):
        return srcpath

    specs = os.path.join(SPECSF_FOLDER, specs)
    if not os.path.isfile(specs):
        return srcpath

    s = evaluator.specs_from_xml(specs)
    ext = {
        'c'       : 'c',
        'c++'     : 'cpp',
        'c#'      : 'cs',
        'java'    : 'java',
        'python'  : 'py',
    }.get(s.language.lower(), None)
    if ext is None:
        return srcpath
    destpath = srcpath[:-4] + f'.{ext}'
    os.rename(srcpath, destpath)
    return destpath
#end def



def delete(file):
    if not isinstance(file, str):
        return
    try:
        if os.path.exists(file):
            os.remove(file)
    except:
        pass
#end def



def str2bool(s):
    if not(isinstance(s, str)):
        return False
    if s.lower() in ['false', '0']:
        return False
    return True
#end def



def begin_clean_old_reports():
    import threading
    t = threading.Thread(target=clean_old_reports)
    t.start()
#end def



def clean_old_reports():
    import datetime, time
    now = int(time.time())
    deadline = now - 3600 * 24
    for f in os.listdir(REPORT_FOLDER):
        path = os.path.join(REPORT_FOLDER, f)
        path = os.path.abspath(path)
        print(f'{path} is ' +
            datetime.date.fromtimestamp(os.path.getmtime(path))\
            .strftime('%Y-%m-%d')
        )
        if os.path.getmtime(path) < deadline:
            delete(path)
#end def



def make_random_name(suffix):
    import hashlib, time
    sha1 = hashlib.sha1()

    sha1.update('File'.encode('utf-8'))
    sha1.update(str(time.time()).encode('utf-8'))
    sha1.update(suffix.encode('utf-8'))
    return sha1.hexdigest() + suffix
#end def



if __name__ == '__main__':
    # app.run()
    app.run(host='0.0.0.0', port=30006, debug=True)
    begin_clean_old_reports()
