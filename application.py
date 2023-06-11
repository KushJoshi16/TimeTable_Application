from flask import (
    Flask, 
    jsonify, 
    request, 
    Response, 
    redirect,
    abort, 
    g,
    render_template,
    session,
    url_for,
    flash
)
import pandas as pd
import generator_algo.algorithm as alg
import generator_algo.output_format as outFmat
import json
import logging
import os
from flask_cors import CORS


class User:

    def __init__(self, id, username, password) -> None:
        self.id = id
        self.username = username
        self.password = password
        
    def __repr__(self) -> str:
        return f'<User : {self.username}>'

admins = []
admins.append(User(id=1,username='admin',password='admin'))
admins.append(User(id=2,username='admin1',password='admin1'))


logger = logging.getLogger('azure.mgmt.resource')
 
application = Flask(__name__)
application.secret_key = 'MYsecretKEy'
CORS(application)
app = application

@app.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
       user = [x for x in admins if x.id == session['user_id']]
       if user:
           g.user = user[0]


@app.route('/')
def index():
    day = [
        'monday',
        'tuesday',
        'wednesday',
        'thursday',
        'friday',
        'saturday'
        ]
    with open('classes/TimeTable.json',"r") as f:
        data = f.read()
    return render_template('index.html', title="page",len = len(day),daylen = alg.dt.CLASS_HOURS,day = day, jsonfile=json.dumps(data))


@app.route('/admin')
def admin():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('admin_page.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method =='POST':
        session.pop('user_id',None)

        username = request.form["username"]
        password = request.form["password"]

        user = [x for x in admins if x.username == username]
        if user and user[0].password == password:
            session['user_id'] = user[0].id
            flash('You were successfully logged in')
            return redirect(url_for('admin'))
        else:
            flash('Invalid credentials')
        return redirect(url_for('login'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id',None)
    if not g.user:
        return redirect(url_for('login'))
    else:
        g.user = None
    flash('You have successfully logged yourself out.')
    return redirect(url_for('login'))


@app.route('/setinputData',methods=['POST'])
def setinputData():
    filepath = None
    if 'file' not in request.files:
        
        flash('Error')
        return redirect(url_for('admin'))
    
    f = request.files['file']
    basepath = os.path.dirname(__file__)
    filepath = os.path.join(basepath,'uploads',f.filename)
    f.save(filepath)
    logger.info("Input data received")
    try:
        data = None
        with open('classes/input.json') as f:
            data = json.load(f)
            
        df = pd.read_csv(filepath)
        df = df.loc[df.astype(str).drop_duplicates().index]
        data['Lectures'] = df.to_dict(orient='records')
        with open('classes/input.json','w') as f:
            json.dump(data,f)

        logger.info("Input data stored in input.json")

        flash('Input Saved')
        return redirect(url_for('admin'))
    except Exception as e:
        logger.error(e)
        flash('Error')
        return redirect(url_for('admin'))



@app.route('/set_inputData',methods=['POST'])
def set_inputData():
    filepath = None
    if 'file' not in request.files:
        abort(400)
    f = request.files['file']
    basepath = os.path.dirname(__file__)
    filepath = os.path.join(basepath,'uploads',f.filename)
    f.save(filepath)
    logger.info("Input data received")
    try:
        data = None
        with open('classes/input.json') as f:
            data = json.load(f)
            
        df = pd.read_csv(filepath)
        df = df.loc[df.astype(str).drop_duplicates().index]
        data['Lectures'] = df.to_dict(orient='records')
        with open('classes/input.json','w') as f:
            json.dump(data,f)

        logger.info("Input data stored in input.json")
        return jsonify(success=True)
    except Exception as e:
        logger.error(e)
        return e
        abort(500)

 
@app.route('/generatetimetable')
def generatetimetable():
    alg.evolutionary_algorithm()
    outFmat.timeTableFromOutput()
    logger.info("Time Table Generated")
    flash('Time Table Genration complete')
    return redirect(url_for('admin'))
 
@app.route('/generate_time_table')
def generate_time_table():
    alg.evolutionary_algorithm()
    outFmat.timeTableFromOutput()
    logger.info("Time Table Generated")
    return jsonify(success=True)

@app.route('/get_time_table')
def get_time_table():
    try:
        f = open('classes/TimeTable.json',"r")
        data = json.load(f)
        f.close()
    except Exception as e:
        logger.error(e)
        try:
            alg.evolutionary_algorithm()
            logger.info("Time Table Regenrated")
            outFmat.timeTableFromOutput()
            f = open('classes/TimeTable.json',"r")
            data = json.load(f)
            f.close()
        except Exception as e:
            logger.error(e)
            abort(500)
    logger.info("Data retrived as data and will be returned as json")
    return jsonify(data)


if __name__ == '__main__':
    app.run()
