#!/usr/bin/env python3

# Base packages
import os
import sys
import uuid
import tempfile
import traceback
import subprocess as sp

# Local packages required before flask
from setup import *
import db

# Flask and friends
from flask import Flask, redirect, url_for, request, render_template
import werkzeug as wz

# Create app
app = Flask(__name__)
db.setup(app)

with app.app_context():
    print(db.Group.query.all())

def execute(exefile, args=[]):
    eargs = [exefile]
    eargs.extend([str(a) for a in args])
    proc = sp.Popen(eargs, stdout=sp.PIPE, stderr=sp.PIPE)
    # try:
    out, err = proc.communicate()
    out = out.decode("utf-8")
    err = err.decode("utf-8")
    # except sp.TimeoutExpired:
    #   proc.kill()
    #   out, err = proc.communicate(timeout=timeout)
    #   return None, None, None
    # except:
    #   out = None
    #   err = None
    return out, err, proc
# end def



@app.route('/')
def root():
    return render_template("index.html", groups=fetch_groups())
#end def



@app.route('/admin')
    return render_template("index.html", groups=fetch_groups())
#end def



@app.route('/group/<int:group_id>')
def upload_code(group_id):
    g = fetch_group(group_id)
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
        evaluator = fetch_evaluator(request.form['evaluator'])
        if not evaluator:
            return redirect("/", code=302)
        specs = evaluator.file
        if len(request.files) > 0 and 'codefile' in request.files:
            f = request.files['codefile']
            path = os.path.join(UPLOAD_FOLDER, wz.utils.secure_filename(f.filename))
            f.save(path)
            sr+= f'Uploaded file {f.filename}\n'
        elif not 'codetext' in request.form:
            return redirect("/", code=302)
        else:
            path = dumptemp(request.form['codetext'])
            sr+= f'Created sourcecode file {path}\n'

        report = evaluate(specs, path)
        delete(path)

        if os.path.isfile(report):
            uri = url_for('static', filename='reports/' + os.path.basename(report))
            return render_template("report.html", reporturi=uri)
        else:
            sr+= f'{report}\n'
            return render_template("form.html", results=sr)
    except:
        return render_template("error.html", traceback=traceback.format_exc())
#end def



# @app.route('/', methods = ['POST', 'GET'])
# def application():
#end def



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


# @app.route('/hello/<name>')
# def hello(name):
    # return f'Hello {name}!'
#end def



def dumptemp(data):
    fd, path = tempfile.mkstemp(prefix='progeval_', suffix='.ext', dir=UPLOAD_FOLDER)
    with open(path, 'w') as f:
        f.write(data)
    os.close(fd)
    return path
#end def



def evaluate(specs, source):
    # specs = os.path.join(SPECSF_FOLDER, f'{specs}.xml')
    specs = os.path.join(SPECSF_FOLDER, specs)
    if not os.path.isfile(specs):
        return None
    ofname = uuid.uuid4().hex
    ofname = os.path.join(REPORT_FOLDER, f'{ofname}.pdf')

    args = [ '-m', 'evaluator', specs, source, '--output', ofname]
    o, e, p = execute('python3', args)
    os.chdir(os.path.dirname(__file__))
    cwd = os.getcwd()
    if p.returncode != 0:
        # return f'\n\ncwd: {cwd}\nretcode: {p.returncode} \nstdout: {o}\nstderr: {e}\n'
        return None
    if not os.path.isfile(ofname):
        # return f'\n\ncwd: {cwd}\n\nstdout: {o}\nstderr: {e}\n{ofname} does not exist\n'
        return None
    # return f'stdout: {o}\nstderr: {e}\n'
    return ofname
#end def



def delete(file):
    if not isinstance(file, str):
        return
    if os.path.exists(file):
        os.remove(file)
#end def



def fetch_groups():
    groups = db.Group.query.order_by(
        db.Group.subject,
        db.Group.number
    ).all()
    return groups
#end def



def fetch_group(group_id):
    # return db.Group.query.get_or_404()
    # return db.Group.query.filter_by(group_id).first()
    return db.Group.query.get(group_id)
#end def



def fetch_evaluator(eid):
    return db.Evaluator.query.get(eid)
#end def



if __name__ == '__main__':
    # app.run()
    app.run(host='0.0.0.0', port=30006, debug=True)

