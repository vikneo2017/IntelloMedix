import os
from flask import Flask, render_template, request, g, url_for, flash, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import datetime
import math
import time
from inference import get_result1, get_result2, get_probability, get_result1_dcm, get_result2_dcm, get_probability_dcm, save_dcmtodb
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from send_mail import send_mail
from send_support import send_support
from werkzeug.utils import secure_filename

# Режим разработки dev и prod
ENV = 'prod'

if ENV == 'dev':
    DATABASE = ''
else:
    DATABASE = ''
    # DATABASE = ''
# конфигурация
DEBUG = True
SECRET_KEY = ''
USERNAME = 'admin'
PASSWORD = '123'
TESTING = False
UPLOAD_FOLDER = '/static/images/userfiles'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if ENV == 'dev':
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = ''
    # app.config['SQLALCHEMY_DATABASE_URI'] = ''
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = SECRET_KEY

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Авторизуйтесь для доступа к закрытым страницам"
login_manager.login_message_category = "success"

engine = create_engine(DATABASE, echo=False)
# db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
db_session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

# global user

class Users(UserMixin, Base):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text, unique=True)
    hpsw = db.Column(db.Text)
    time = db.Column(db.Integer)
    nameorg = db.Column(db.Text)
    address = db.Column(db.Text)
    emailorg = db.Column(db.Text)
    tel = db.Column(db.Text)
    website = db.Column(db.Text)

    def __init__(self, name, email, hpsw, time, nameorg, address, emailorg, tel, website):
        self.name = name
        self.email = email
        self.hpsw = hpsw
        self.time = time
        self.nameorg = nameorg
        self.address = address
        self.emailorg = emailorg
        self.tel = tel
        self.website = website

    def __repr__(self):
        return '<User %r>' % (self.id)

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, primary_key=True)
    orderEmail = db.Column(db.Text)
    orderPhone = db.Column(db.Text)
    order = db.Column(db.Text)
    date = db.Column(db.Text)

    def __init__(self, orderEmail, orderPhone, order, date):
        self.orderEmail = orderEmail
        self.orderPhone = orderPhone
        self.order = order
        self.date = date

class Support(db.Model):
    __tablename__ = 'support'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    email = db.Column(db.Text)
    theme = db.Column(db.Text)
    message = db.Column(db.Text)
    screenshot = db.Column(db.LargeBinary)
    date = db.Column(db.Text)

    def __init__(self, name, email, theme, message, screenshot, date):
        self.name = name
        self.email = email
        self.theme = theme
        self.message = message
        self.screenshot = screenshot
        self.date = date

class Dcmimages(db.Model):
    __tablename__ = 'dcmimages'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    dcmimage = db.Column(db.LargeBinary)
    date = db.Column(db.Text)

    def __init__(self, userid, dcmimage, date):
        self.userid = userid
        self.dcmimage = dcmimage
        self.date = date

class UserStatus(db.Model):
    __tablename__ = 'userstatus'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    status = db.Column(db.Text)
    ostatok = db.Column(db.Text)
    date_refresh = db.Column(db.Text)

    def __init__(self, userid, status, ostatok, date_refresh):
        self.userid = userid
        self.status = status
        self.ostatok = ostatok
        self.date_refresh = date_refresh

class UserRecords(db.Model):
    __tablename__ = 'userrecords'
    id = db.Column(db.Integer, primary_key=True)
    userid = db.Column(db.Integer)
    namepat = db.Column(db.Text)
    surnamepat = db.Column(db.Text)
    birthdate = db.Column(db.Text)
    specialist = db.Column(db.Text)
    date = db.Column(db.Text)
    result = db.Column(db.Text)

    def __init__(self, userid, namepat, surnamepat, birthdate, specialist, date, result):
        self.userid = userid
        self.namepat = namepat
        self.surnamepat = surnamepat
        self.birthdate = birthdate
        self.specialist = specialist
        self.date = date
        self.result = result

@login_manager.user_loader
def load_user(id):
   print('user id:'+str(id))
   return db_session.query(Users).get(int(id))

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    if request.method == 'POST':
        return render_template('index.html')

@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "GET":
        render_template("login.html", title="Авторизация")
    if request.method == "POST":
        global user
        user = db_session.query(Users).filter_by(email=request.form['email']).first()
        if user != None and check_password_hash(user.hpsw, request.form['psw']):
            session['logged_in'] = True
            rm = True if request.form.get('remainme') else False
            login_user(user, remember=rm)
            if current_user.id == 1:
                return redirect(url_for('admin'))
            return redirect(url_for('profile'))
        else:
            flash("Неверная пара логин/пароль", "error")
            redirect(url_for('login'))
    return render_template("login.html", title="Авторизация")

@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    logout_user()
    return redirect(url_for('login'))

@app.route("/admin", methods=['GET', 'POST'])
@login_required
def admin():
    if request.method == "GET":
        if current_user.id == 1:
            return render_template('admin.html')
        else:
            return redirect(url_for('index'))
    if request.method == "POST":
        if current_user.id != 1:
            flash("У вас нет прав администратора ресурса для активации пользователей", "error")
            return redirect(url_for('/'))
        else:
            return render_template('admin.html')
    else:
        flash("Произошла ошибка", "error")
        return render_template('admin.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    if request.method == "POST":
        # session.pop('_flashes', None)
        user_check = db_session.query(Users).filter_by(email=request.form['email']).first()
        if user_check != None:
            flash("Пользователь с таким email уже зарегистрирован в системе", "error")
            return redirect(url_for('register'))
        else:
            if len(request.form['name']) > 2 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and len(request.form['nameorg']) > 4 and len(request.form['address']) > 4\
                and len(request.form['emailorg']) > 4 and len(request.form['tel']) > 4 and len(request.form['website']) > 4\
                and request.form['psw'] == request.form['psw2']:
                hash = generate_password_hash(request.form['psw'])
                tm = math.floor(time.time())
                if db_session.query(Users).filter(Users.email == request.form['email']).count() == 0:
                    user = Users(name=request.form['name'], email=request.form['email'], hpsw=hash,
                                 nameorg=request.form['nameorg'], address=request.form['address'],
                                 emailorg=request.form['emailorg'], tel=request.form['tel'],
                                 website=request.form['website'], time=tm)
                    db_session.add(user)
                    db_session.commit()
                    login_user(user)
                    return redirect(url_for('admin'))
                else:
                    flash("Ошибка при добавлении в БД. Проверьте правильность заполнения полей", "error")
                    return render_template('register.html')
            else:
                flash("Ошибка! Проверьте правильность заполнения полей", "error")
                return render_template('register.html')
        return render_template('register.html')

@app.route("/activation", methods=['GET', 'POST'])
@login_required
def activation():
    if request.method == "GET":
        return render_template('activation.html')
    if request.method == "POST":
        # session.pop('_flashes', None)
        if current_user.id != 1:
            flash("У вас нет прав администратора ресурса для активации пользователей", "error")
            return redirect(url_for('activation'))
        else:
            if len(request.form['userid']) > 0 and len(request.form['status']) > 2 \
                and len(request.form['ostatok']) > 0 and len(request.form['date_activation']) > 0:
                if request.form['status'] == 'Test':
                    ostatok = 'Не ограничено'
                elif request.form['status'] == 'PaidPack':
                    ostatok = request.form['ostatok']
                elif request.form['status'] == 'PaidDate':
                    ostatok = 'До {} не ограничено'.format(str(request.form['date_activation']))
                else:
                    return redirect(url_for('activation'))
                # Проверяем наличие пользователя в базе:
                if db_session.query(UserStatus).filter(UserStatus.userid == str(request.form['userid'])).first() is None:
                    userstatus = UserStatus(userid=request.form['userid'], status=request.form['status'],
                                    ostatok=ostatok, date_refresh=request.form['date_activation'])
                    db_session.add(userstatus)
                    db_session.commit()
                else:
                    new_status = request.form['status']
                    if new_status == 'Test':
                        new_ostatok = 'Не ограничено'
                    elif new_status == 'PaidPack':
                        new_ostatok = request.form['ostatok']
                    else:
                        new_ostatok = 'До {} не ограничено'.format(request.form['date_activation'])
                    new_date_refresh = request.form['date_activation']
                    db_session.query(UserStatus).filter(UserStatus.userid == str(request.form['userid'])).update({"status": new_status})
                    db_session.query(UserStatus).filter(UserStatus.userid == str(request.form['userid'])).update({"ostatok": new_ostatok})
                    db_session.query(UserStatus).filter(UserStatus.userid == str(request.form['userid'])).update({"date_refresh": new_date_refresh})
                    db_session.commit()
                login_user(user)
                return render_template('admin.html')
            else:
                flash("Ошибка при добавлении в БД. Проверьте правильность заполнения полей", "error")
                return render_template('activation.html')
    else:
        flash("Произошла ошибка", "error")
        return render_template('activation.html')

@app.route('/check')
@login_required
def check():
    return render_template('check.html')

@app.route('/proverka', methods=['GET', 'POST'])
@login_required
def proverka():
    if request.method == 'GET':
        return redirect(url_for('check'))
    if request.method == 'POST':
        check_email = request.form['email']
        if db_session.query(Users).filter(Users.email == check_email).first() is None:
            userid = 'Не зарегистрировано'
            name = 'Не зарегистрировано'
            email = 'Не зарегистрировано'
            nameorg = 'Не зарегистрировано'
            address = 'Не зарегистрировано'
            emailorg = 'Не зарегистрировано'
            tel = 'Не зарегистрировано'
            website = 'Не зарегистрировано'
            status = 'Не зарегистрировано'
            ostatok = 'Не зарегистрировано'
            date_refresh = 'Не зарегистрировано'
        else:
            userid = db_session.query(Users).filter(Users.email == check_email).first().id
            name = db_session.query(Users).filter(Users.email == check_email).first().name
            email = check_email
            nameorg = db_session.query(Users).filter(Users.email == check_email).first().nameorg
            address = db_session.query(Users).filter(Users.email == check_email).first().address
            emailorg = db_session.query(Users).filter(Users.email == check_email).first().emailorg
            tel = db_session.query(Users).filter(Users.email == check_email).first().tel
            website = db_session.query(Users).filter(Users.email == check_email).first().website
            status = db_session.query(UserStatus).filter(UserStatus.userid == userid).first().status
            ostatok = db_session.query(UserStatus).filter(UserStatus.userid == userid).first().ostatok
            date_refresh = db_session.query(UserStatus).filter(UserStatus.userid == userid).first().date_refresh
        return render_template('proverka.html', userid=userid, name=name, email=email, nameorg=nameorg, address=address, emailorg=emailorg, tel=tel, website=website, status=status, ostatok=ostatok, date_refresh=date_refresh)

@app.route('/profile')
@login_required
def profile():
    session['logged_in'] = True
    email = current_user.email
    nameorg = current_user.nameorg
    address = current_user.address
    tel = current_user.tel
    website = current_user.website
    if db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first() is None:
        balance = '0'
        tarif = 'У вас не подключен тарифный план'
    else:
        balance = db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().ostatok
        status = db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().status
        if status == 'Test':
            tarif = 'Режим тестирования'
        elif status == 'PaidPack':
            tarif = 'Ваш тариф: "100 протоколов"'
        elif status == 'PaidDate':
            tarif = 'Ваш тариф: "Безлимитный"'
        else:
            tarif = 'Ваш тариф не определен'
    return render_template('profile.html', email=email, nameorg=nameorg, address=address, tel=tel, website=website, balance=balance,
                           tarif=tarif)

@app.route('/story')
@login_required
def story():
    if db_session.query(UserRecords).filter(UserRecords.userid == current_user.id).first() is None:
        tabl = 'Нет протоколов'
    else:
        tabl = db_session.query(UserRecords).filter(UserRecords.userid == current_user.id).all()
    return render_template('story.html', tabl=tabl)

@app.route('/start', methods=['GET', 'POST'])
@login_required
def start():
    if request.method == 'GET':
        if db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first() is None:
            balance = '0'
        else:
            balance = db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().ostatok
        return render_template('start.html', balance=balance)
    if request.method == 'POST':
        return render_template('start.html')

@app.route('/tarifs', methods=['GET', 'POST'])
def tarifs():
    if request.method == 'GET':
        return render_template('tarifs.html')
    if request.method == 'POST':
        return render_template('tarifs.html')

@app.route('/demo', methods=['GET', 'POST'])
def demo():
    if request.method == "POST":
        session.pop('_flashes', None)
        order = 'DEMO'
        now = datetime.datetime.now()
        datenow = now.strftime("%d-%m-%Y %H:%M")
        if len(request.form['orderEmail']) > 4 and len(request.form['orderPhone']) > 4 :
            res = Orders(orderEmail=request.form['orderEmail'], orderPhone=request.form['orderPhone'], order=order, date=datenow)
            db_session.add(res)
            db_session.commit()
            send_mail(orderEmail=request.form['orderEmail'], orderPhone=request.form['orderPhone'], order=order, date=datenow)
            return redirect(url_for('demosuccess'))
        else:
            flash("Неверно заполнены поля", "error")
            return redirect(url_for('demo'))
    return render_template("demo.html", title="Получение демо-доступа")

@app.route('/demo2', methods=['GET', 'POST'])
@login_required
def demo2():
    if request.method == "POST":
        session.pop('_flashes', None)
        order = 'DEMO'
        now = datetime.datetime.now()
        datenow = now.strftime("%d-%m-%Y %H:%M")
        if len(request.form['orderEmail']) > 4 and len(request.form['orderPhone']) > 4 :
            res = Orders(orderEmail=request.form['orderEmail'], orderPhone=request.form['orderPhone'], order=order, date=datenow)
            db_session.add(res)
            db_session.commit()
            send_mail(orderEmail=request.form['orderEmail'], orderPhone=request.form['orderPhone'], order=order,
                      date=datenow)
            return redirect(url_for('demosuccess2'))
        else:
            flash("Неверно заполнены поля", "error")
            return redirect(url_for('demo2'))
    return render_template("demo2.html", title="Получение демо-доступа")

@app.route('/demosuccess', methods=['GET', 'POST'])
def demosuccess():
    if request.method == 'GET':
        return render_template('demo_success.html')
    if request.method == 'POST':
        return render_template('demo_success.html')

@app.route('/demosuccess2', methods=['GET', 'POST'])
@login_required
def demosuccess2():
    if request.method == 'GET':
        return render_template('demo_success2.html')
    if request.method == 'POST':
        return render_template('demo_success2.html')

@app.route('/buy', methods=['GET', 'POST'])
def buy():
    if request.method == "GET":
        render_template("buy.html", title="Получение платного доступа")
    if request.method == "POST":
        session.pop('_flashes', None)
        order = 'BUY'
        now = datetime.datetime.now()
        datenow = now.strftime("%d-%m-%Y %H:%M")
        if len(request.form['orderEmail']) > 4 and len(request.form['orderPhone']) > 4:
            res = Orders(orderEmail=request.form['orderEmail'], orderPhone=request.form['orderPhone'], order=order,
                         date=datenow)
            db_session.add(res)
            db_session.commit()
            send_mail(orderEmail=request.form['orderEmail'], orderPhone=request.form['orderPhone'], order=order,
                      date=datenow)
            return redirect(url_for('buysuccess'))
        else:
            flash("Неверно заполнены поля", "error")
            return redirect(url_for('buy'))
    return render_template("buy.html", title="Покупка доступа")

@app.route('/buy2', methods=['GET', 'POST'])
@login_required
def buy2():
    if request.method == "GET":
        render_template("buy2.html", title="Получение доступа по тарифу")
    if request.method == "POST":
        session.pop('_flashes', None)
        order = 'BUY'
        now = datetime.datetime.now()
        datenow = now.strftime("%d-%m-%Y %H:%M")
        if len(request.form['orderEmail']) > 4 and len(request.form['orderPhone']) > 4:
            res = Orders(orderEmail=request.form['orderEmail'], orderPhone=request.form['orderPhone'], order=order,
                         date=datenow)
            db_session.add(res)
            db_session.commit()
            send_mail(orderEmail=request.form['orderEmail'], orderPhone=request.form['orderPhone'], order=order,
                      date=datenow)
            return redirect(url_for('buysuccess2'))
        else:
            flash("Неверно заполнены поля", "error")
            return redirect(url_for('buy2'))
    return render_template("buy2.html", title="Получение демо-доступа")

@app.route('/buysuccess', methods=['GET', 'POST'])
def buysuccess():
    if request.method == 'GET':
        return render_template('buy_success.html')
    if request.method == 'POST':
        return render_template('buy_success.html')

@app.route('/buysuccess2', methods=['GET', 'POST'])
@login_required
def buysuccess2():
    if request.method == 'GET':
        return render_template('buy_success2.html')
    if request.method == 'POST':
        return render_template('buy_success2.html')

@app.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == "POST":
        session.pop('_flashes', None)
        now = datetime.datetime.now()
        datenow = now.strftime("%d-%m-%Y %H:%M")
        file = request.files['file']
        screenshot = file.read()
        file.close()
        if len(request.form['name']) > 4 and len(request.form['email']) > 4:
            res = Support(name=request.form['name'], email=request.form['email'], theme=request.form['theme'],
                          message=request.form['message'], date=datenow, screenshot=screenshot)
            db_session.add(res)
            db_session.commit()
            send_support(name=request.form['name'], email=request.form['email'], theme=request.form['theme'],
                         message=request.form['message'], date=datenow)
            return redirect(url_for('support_success'))
        else:
            flash("Неверно заполнены поля", "error")
            return redirect(url_for('support'))
    return render_template("support.html", title="Запрос в техподдержку")

@app.route('/support_success', methods=['GET', 'POST'])
def support_success():
    if request.method == 'GET':
        return render_template('support_success.html')
    if request.method == 'POST':
        return render_template('support_success.html')

@app.route('/contact2', methods=['GET', 'POST'])
@login_required
def contact2():
    if request.method == 'GET':
        return render_template('contact2.html')
    if request.method == 'POST':
        return render_template('contact2.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'GET':
        return render_template('contact.html')
    if request.method == 'POST':
        return render_template('contact.html')

@app.route('/index2', methods=['GET', 'POST'])
@login_required
def index2():
    if request.method == 'GET':
        return render_template('index2.html')
    if request.method == 'POST':
        return render_template('index2.html')

@app.route('/tarifs2', methods=['GET', 'POST'])
@login_required
def tarifs2():
    if request.method == 'GET':
        return render_template('tarifs2.html')
    if request.method == 'POST':
        return render_template('tarifs2.html')

@app.route('/support2', methods=['GET', 'POST'])
@login_required
def support2():
    if request.method == "POST":
        session.pop('_flashes', None)
        now = datetime.datetime.now()
        datenow = now.strftime("%d-%m-%Y %H:%M")
        file = request.files['file']
        screenshot = file.read()
        file.close()
        if len(request.form['name']) > 4 and len(request.form['email']) > 4:
            res = Support(name=request.form['name'], email=request.form['email'], theme=request.form['theme'],
                          message=request.form['message'], date=datenow, screenshot=screenshot)
            db_session.add(res)
            db_session.commit()
            send_support(name=request.form['name'], email=request.form['email'], theme=request.form['theme'],
                         message=request.form['message'], date=datenow)
            return redirect(url_for('support_success2'))
        else:
            flash("Неверно заполнены поля", "error")
            return redirect(url_for('support2'))
    return render_template("support2.html", title="Запрос в техподдержку")

@app.route('/support_success2', methods=['GET', 'POST'])
def support_success2():
    if request.method == 'GET':
        return render_template('support_success2.html')
    if request.method == 'POST':
        return render_template('support_success2.html')

@app.route('/imganalis')
@login_required
def imganalis():
    return render_template('imganalis.html')

@app.route('/dcmanalis')
@login_required
def dcmanalis():
    return render_template('dcmanalis.html')

@app.route('/result_ct', methods=['GET', 'POST'])
@login_required
def result_ct():
    if request.method == 'GET':
        return redirect(url_for('start'))
    if request.method == 'POST':
        medname = request.form['medname']
        if len(medname)==0:
            medname = ''
        nameequip = request.form['nameequip']
        if len(nameequip)==0:
            nameequip = ''
        number = request.form['number']
        if len(number)==0:
            number = ''
        surnamepat = request.form['surnamepat']
        if len(surnamepat)==0:
            surnamepat = ''
        namepat = request.form['namepat']
        if len(namepat)==0:
            namepat = ''
        middlenamepat = request.form['middlenamepat']
        if len(middlenamepat) == 0:
            middlenamepat = ''
        sex = request.form['sex']
        if len(sex) == 0:
            sex = ''
        birthdate = request.form['birthdate']
        if len(birthdate) == 0:
            birthdate = ''
        research = request.form['research']
        if len(research) == 0:
            research = ''
        # age = request.form['age']
        if len(birthdate) == 0:
            age = ''
        else:
            from datetime import timedelta
            bdate = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
            today = datetime.datetime.now()
            age = (today - bdate)//timedelta(days=365.2425)
        comments = request.form['comments']
        if len(comments) == 0:
            comments = ''
        now = datetime.datetime.now()
        datenow = now.strftime("%d-%m-%Y %H:%M")
        file = request.files['file']
        ## ЗДЕСЬ БЫЛИ ПРОБЛЕМЫ
        # create the folders when setting up your app
        os.makedirs(os.path.join(app.instance_path, 'userfiles'), exist_ok=True)
        tm = math.floor(time.time())
        filename = str(current_user.id)+'-'+str(tm)+'.dcm'
        # сохраняем первый файл
        ### Сохраняем файл в директорию
        file.save(os.path.join(app.instance_path, 'userfiles', secure_filename(filename)))
        filepath=os.path.join(app.instance_path, 'userfiles', secure_filename(filename))
        ### Сохраняем файл в базу данных
        output_todb = save_dcmtodb(filepath)
        dcmimage = Dcmimages(userid=current_user.id, dcmimage=output_todb, date=tm)
        db_session.add(dcmimage)
        db_session.commit()
        # Делаем предсказание
        resultat1 = get_result1_dcm(file=filepath)
        ### Извлекаем файл из БД
        # output=db_session.query(Dcmimages).order_by(Dcmimages.date.desc()).filter_by(userid=current_user.id).first().dcmimage
        # resultat1 = get_result1_fromdb(file=output)
        # сохраняем второй файл
        ### Сохраняем файл в директорию
        file2 = request.files['file2']
        filename2 = str(current_user.id) + '-' + str(tm) + '-2.dcm'
        file2.save(os.path.join(app.instance_path, 'userfiles', secure_filename(filename2)))
        filepath2 = os.path.join(app.instance_path, 'userfiles', secure_filename(filename2))
        ### Сохраняем файл в базу данных
        output_todb = save_dcmtodb(filepath2)
        tm2 = math.floor(time.time())
        dcmimage2 = Dcmimages(userid=current_user.id, dcmimage=output_todb, date=tm2)
        db_session.add(dcmimage2)
        db_session.commit()
        # Делаем предсказания
        resultat2 = get_result1_dcm(file=filepath2)
        if resultat1 == 'Yes':
            leftnopatology = ' '
            leftpatology = '+'
        else:
            leftnopatology = '+'
            leftpatology = ' '
        if resultat2 == 'Yes':
            rightnopatology = ' '
            rightpatology = '+'
        else:
            rightnopatology = '+'
            rightpatology = ' '
        if resultat1 == 'Yes' or resultat2 == 'Yes':
            resultat3 = get_result2_dcm(file=filepath)
            resultat4 = get_result2_dcm(file=filepath2)
            itog = max(3, int(resultat3), int(resultat4))
            zakl = {'1': 'Объемные образования в молочной железе не выявлены - варианты возрастной нормы. Категория BI-RADS: 1',
                '2': 'Нет факторов, указывающих на злокачественный процесс. Категория BI-RADS: 2',
                '3': 'Вероятно доброкачественные образования, требующие повторного УЗИ через 3-6 месяцев или динамического наблюдения в процессе выполнения лечебных мероприятий. Категория BI-RADS: 3',
                '4': 'Подозрение на злокачественное образование, требующее обязательного выполнения пункционной биопсии. Категория BI-RADS: 4',
                '5': 'Выявленное образование имеет типичные УЗ-признаки рака молочной железы. При получении доброкачественных или сомнительных результатов биопсии необходим пересмотр гистологического материала. Категория BI-RADS: 5'}
            vyvod = zakl[str(itog)]
            recomendation_dict = {
                '1': 'Рекомендуется проведение плановых исследований согласно возрасту',
                '2': 'Рекомендуется проведение плановых исследований согласно возрасту.',
                '3': 'Рекомендуется повторное УЗИ через 3-6 месяцев или динамическое наблюдение в процессе выполнения лечебных мероприятий',
                '4': 'Обязательно выполнить пункционную биопсию',
                '5': 'При получении доброкачественных или сомнительных результатов биопсии необходим пересмотр гистологического материала.'}
            recomendation = recomendation_dict[str(itog)]
        else:
            resultat3 = get_result2_dcm(file=filepath)
            resultat4 = get_result2_dcm(file=filepath2)
            if int(resultat3) >= 3 or int(resultat4) >=3:
                itog = 2
            else:
                itog = max(1, int(resultat3), int(resultat4))
            zakl = {
                '1': 'Объемные образования в молочной железе не выявлены - варианты возрастной нормы. Категория BI-RADS: 1',
                '2': 'Нет факторов, указывающих на злокачественный процесс. Категория BI-RADS: 2',
                '3': 'Вероятно доброкачественные образования, требующие повторного УЗИ через 3-6 месяцев или динамического наблюдения в процессе выполнения лечебных мероприятий. Категория BI-RADS: 3',
                '4': 'Подозрение на злокачественное образование, требующее обязательного выполнения пункционной биопсии. Категория BI-RADS: 4',
                '5': 'Выявленное образование имеет типичные УЗ-признаки рака молочной железы. При получении доброкачественных или сомнительных результатов биопсии необходим пересмотр гистологического материала. Категория BI-RADS: 5'}
            vyvod = zakl[str(itog)]
            recomendation_dict = {
                '1': 'Рекомендуется проведение плановых исследований согласно возрасту',
                '2': 'Рекомендуется проведение плановых исследований согласно возрасту.',
                '3': 'Рекомендуется повторное УЗИ через 3-6 месяцев или динамическое наблюдение в процессе выполнения лечебных мероприятий',
                '4': 'Обязательно выполнить пункционную биопсию',
                '5': 'При получении доброкачественных или сомнительных результатов биопсии необходим пересмотр гистологического материала.'}
            recomendation = recomendation_dict[str(itog)]
        proba_left = str(round(float(get_probability_dcm(file=filepath))* 100, 2))+'%'
        proba_right = str(round(float(get_probability_dcm(file=filepath2))* 100, 2))+'%'
        nameorg=current_user.nameorg
        address=current_user.address
        emailorg=current_user.emailorg
        tel=current_user.tel
        website=current_user.website
        os.remove(filepath)
        os.remove(filepath2)
        ### Делаем запись в БД о полученном протоколе:
        userrecord = UserRecords(userid=current_user.id, namepat=namepat, surnamepat=surnamepat, birthdate=birthdate,
                                 specialist=medname, date=datenow, result=vyvod)
        db_session.add(userrecord)
        db_session.commit()
        ### Изменяем баланс протоколов
        if db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().status != 'Test'\
                or db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().status != 'PaidDate':
            new_balance = int(db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().ostatok) - 1
            db_session.query(UserStatus).update({"ostatok": new_balance})
            db_session.commit()
        return render_template('result.html', data=datenow, medname=medname, nameequip=nameequip, number=number,
                               surnamepat=surnamepat, namepat=namepat, middlenamepat=middlenamepat,
                               sex=sex, birthdate=birthdate, age=age, research=research,
                               comments=comments, resultat1=resultat1, resultat2=resultat2,
                               leftnopatology=leftnopatology, leftpatology=leftpatology,
                               rightnopatology=rightnopatology, rightpatology=rightpatology, vyvod=vyvod, recomendation=recomendation,
                               proba_left=proba_left, proba_right=proba_right,
                               nameorg=nameorg, address=address, emailorg=emailorg, tel=tel, website=website)

@app.route('/result', methods=['GET', 'POST'])
@login_required
def result():
    if request.method == 'GET':
        return redirect(url_for('start'))
    if request.method == 'POST':
        medname = request.form['medname']
        if len(medname)==0:
            medname = ''
        nameequip = request.form['nameequip']
        if len(nameequip)==0:
            nameequip = ''
        number = request.form['number']
        if len(number)==0:
            number = ''
        surnamepat = request.form['surnamepat']
        if len(surnamepat)==0:
            surnamepat = ''
        namepat = request.form['namepat']
        if len(namepat)==0:
            namepat = ''
        middlenamepat = request.form['middlenamepat']
        if len(middlenamepat) == 0:
            middlenamepat = ''
        sex = request.form['sex']
        if len(sex) == 0:
            sex = ''
        birthdate = request.form['birthdate']
        if len(birthdate) == 0:
            birthdate = ''
        research = request.form['research']
        if len(research) == 0:
            research = ''
        if len(birthdate) == 0:
            age = ''
        else:
            from datetime import timedelta
            bdate = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
            today = datetime.datetime.now()
            age = (today - bdate)//timedelta(days=365.2425)
        comments = request.form['comments']
        if len(comments) == 0:
            comments = ''
        now = datetime.datetime.now()
        datenow = now.strftime("%d-%m-%Y %H:%M")
        # сохраняем первый файл
        file = request.files['file']
        image = file.read()
        ### Сохраняем файл в базу данных
        tm = math.floor(time.time())
        dcmimage = Dcmimages(userid=current_user.id, dcmimage=image, date=tm)
        db_session.add(dcmimage)
        db_session.commit()
        # сохраняем второй файл
        file2 = request.files['file2']
        image2 = file2.read()
        ### Сохраняем файл в базу данных
        tm2 = math.floor(time.time())
        dcmimage2 = Dcmimages(userid=current_user.id, dcmimage=image, date=tm2)
        db_session.add(dcmimage2)
        db_session.commit()
        if str(image)=='b\'\'' and str(image2)=='b\'\'':
            flash("Внимание!Не загружены изображения для левой и правой груди")
            return redirect(url_for('imganalis'))
        elif str(image)=='b\'\'':
            flash("Внимание!Не загружено изображение для левой груди")
            return redirect(url_for('imganalis'))
        elif str(image2)=='b\'\'':
            flash("Внимание!Не загружено изображение для правой груди")
            return redirect(url_for('imganalis'))
        else:
            resultat1 = get_result1(image_bytes=image)
            resultat2 = get_result1(image_bytes=image2)
            if resultat1 == 'Yes':
                leftnopatology = ' '
                leftpatology = '+'
            else:
                leftnopatology = '+'
                leftpatology = ' '
            if resultat2 == 'Yes':
                rightnopatology = ' '
                rightpatology = '+'
            else:
                rightnopatology = '+'
                rightpatology = ' '
            if resultat1 == 'Yes' or resultat2 == 'Yes':
                resultat3 = get_result2(image_bytes=image)
                resultat4 = get_result2(image_bytes=image2)
                itog = max(3, int(resultat3), int(resultat4))
                zakl = {'1': 'Объемные образования в молочной железе не выявлены - варианты возрастной нормы. Категория BI-RADS: 1',
                    '2': 'Нет факторов, указывающих на злокачественный процесс. Категория BI-RADS: 2',
                    '3': 'Вероятно доброкачественные образования, требующие повторного УЗИ через 3-6 месяцев или динамического наблюдения в процессе выполнения лечебных мероприятий. Категория BI-RADS: 3',
                    '4': 'Подозрение на злокачественное образование, требующее обязательного выполнения пункционной биопсии. Категория BI-RADS: 4',
                    '5': 'Выявленное образование имеет типичные УЗ-признаки рака молочной железы. При получении доброкачественных или сомнительных результатов биопсии необходим пересмотр гистологического материала. Категория BI-RADS: 5'}
                vyvod = zakl[str(itog)]
                recomendation_dict = {
                    '1': 'Рекомендуется проведение плановых исследований согласно возрасту',
                    '2': 'Рекомендуется проведение плановых исследований согласно возрасту.',
                    '3': 'Рекомендуется повторное УЗИ через 3-6 месяцев или динамическое наблюдение в процессе выполнения лечебных мероприятий',
                    '4': 'Обязательно выполнить пункционную биопсию',
                    '5': 'При получении доброкачественных или сомнительных результатов биопсии необходим пересмотр гистологического материала.'}
                recomendation = recomendation_dict[str(itog)]
            else:
                resultat3 = get_result2(image_bytes=image)
                resultat4 = get_result2(image_bytes=image2)
                if int(resultat3) >= 3 or int(resultat4) >=3:
                    itog = 2
                else:
                    itog = max(1, int(resultat3), int(resultat4))
                zakl = {
                    '1': 'Объемные образования в молочной железе не выявлены - варианты возрастной нормы. Категория BI-RADS: 1',
                    '2': 'Нет факторов, указывающих на злокачественный процесс. Категория BI-RADS: 2',
                    '3': 'Вероятно доброкачественные образования, требующие повторного УЗИ через 3-6 месяцев или динамического наблюдения в процессе выполнения лечебных мероприятий. Категория BI-RADS: 3',
                    '4': 'Подозрение на злокачественное образование, требующее обязательного выполнения пункционной биопсии. Категория BI-RADS: 4',
                    '5': 'Выявленное образование имеет типичные УЗ-признаки рака молочной железы. При получении доброкачественных или сомнительных результатов биопсии необходим пересмотр гистологического материала. Категория BI-RADS: 5'}
                vyvod = zakl[str(itog)]
                recomendation_dict = {
                    '1': 'Рекомендуется проведение плановых исследований согласно возрасту',
                    '2': 'Рекомендуется проведение плановых исследований согласно возрасту.',
                    '3': 'Рекомендуется повторное УЗИ через 3-6 месяцев или динамическое наблюдение в процессе выполнения лечебных мероприятий',
                    '4': 'Обязательно выполнить пункционную биопсию',
                    '5': 'При получении доброкачественных или сомнительных результатов биопсии необходим пересмотр гистологического материала.'}
                recomendation = recomendation_dict[str(itog)]
            proba_left = str(round(float(get_probability(image_bytes=image))* 100, 2))+'%'
            proba_right = str(round(float(get_probability(image_bytes=image2))* 100, 2))+'%'
            nameorg=current_user.nameorg
            address=current_user.address
            emailorg=current_user.emailorg
            tel=current_user.tel
            website=current_user.website
            ### Делаем запись в БД о полученном протоколе:
            userrecord = UserRecords(userid=current_user.id, namepat=namepat, surnamepat=surnamepat,
                                     birthdate=birthdate,
                                     specialist=medname, date=datenow, result=vyvod)
            db_session.add(userrecord)
            db_session.commit()
            ### Изменяем баланс протоколов
            if db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().status != 'Test'\
                and db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().status != 'PaidDate':
                new_balance = int(db_session.query(UserStatus).filter(UserStatus.userid == current_user.id).first().ostatok) - 1
                db_session.query(UserStatus).update({"ostatok": new_balance})
                db_session.commit()
        return render_template('result.html', data=datenow, medname=medname, nameequip=nameequip, number=number,
                               surnamepat=surnamepat, namepat=namepat, middlenamepat=middlenamepat,
                               sex=sex, birthdate=birthdate, age=age, research=research,
                               comments=comments, resultat1=resultat1, resultat2=resultat2,
                               leftnopatology=leftnopatology, leftpatology=leftpatology,
                               rightnopatology=rightnopatology, rightpatology=rightpatology, vyvod=vyvod, recomendation=recomendation,
                               proba_left=proba_left, proba_right=proba_right,
                               nameorg=nameorg, address=address, emailorg=emailorg, tel=tel, website=website)

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv('PORT', 5000))








