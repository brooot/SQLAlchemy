from flask import Flask, url_for, request, render_template, redirect, make_response
from flask_sqlalchemy import SQLAlchemy
import pymysql

pymysql.install_as_MySQLdb()

app = Flask(__name__)

# 给Flask对象app指定数据库连接参数
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:xzl1122@localhost:3306/flask'

# 指定让SQLAlchemy自动追踪程序的修改,如果改成 True 会占用大量的内存,建议关闭
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# 指定执行完操作之后自动提交
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# 创建SQLAlchemy的实例
# db是SQLAlchemy的实例,表示程序正在使用的数据库,同时也获得了SQLAlchemy中的所有功能
db = SQLAlchemy(app)


# 创建模型类 - Models
# 创建 Users 类, 映射到表中叫 users 表
# 创建字段 : id ,主键, 自增
# 创建字段 : username , 长度为80的字符串,不允许为空, 必须唯一
# 创建字段 : age ,整数,允许为空
# 创建字段 : email ,长度为120的字符串, 必须唯一
class Users(db.Model):
    __tablename__ = "users"  # type: str
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    age = db.Column(db.Integer, nullable=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, age, email):
        self.username = username
        self.age = age
        self.email = email

    def __repr__(self):
        return "<Users: %r>" % self.username


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    sname = db.Column(db.String(30), nullable=False)
    sage = db.Column(db.Integer)

    def __init__(self, sname, sage):
        self.sname = sname
        self.sage = sage

    def __repr__(self):
        return "<Student %r>" % self.sname


class Teacher(db.Model):
    __tablename__ = "teacher"
    id = db.Column(db.Integer, primary_key=True)
    tname = db.Column(db.String(30), nullable=False)
    tage = db.Column(db.Integer)

    # 增加一列 : course_id ,外键列, 要引用自主键表(course)的主键列(id)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))

    def __init__(self, tname, tage):
        self.tname = tname
        self.tage = tage

    def __repr__(self):
        return "<Teacher %r>" % self.tname


class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)
    cname = db.Column(db.String(30))

    # 反向引用: 返回与当前课程相关的teacher列表
    # backref: 定义反向关系,本质上会向Teacher实体中增加一个course属性,
    # 该属性可以替代course_id来访问Course模型,此时获的到的是'模型对象',而不是外键值
    # 相当于在Teacher 中再增加一个属性 "course"
    teachers = db.relationship('Teacher', backref='course', lazy="dynamic")

    def __init__(self, cname):
        self.cname = cname

    def __repr__(self):
        return "<Course %r>" % self.cname


# 清空 所有表 和 所有表项记录
# db.drop_all()


# 将创建好的实体类映射回数据库
db.create_all()


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('01-register.html')
    else:
        uname = request.form.get('uname')
        uage = request.form['uage']
        uemail = request.form['uemail']

        # 创建Users对象
        users = Users(uname, uage, uemail)

        if db.session.query(Users).filter_by(username=uname).all():

            print("用户名重复!")
            return "用户名重复!"
        elif db.session.query(Users).filter_by(email=uemail).all():
            print("邮箱重复!")
            return "邮箱重复!"

        else:
            print("--------------------注册成功------------------------")

            # 将对象通过db.session.add()插入到数据库
            db.session.add(users)

            # 提交插入操作
            # db.session.commit()
            resp = redirect("/query_all")
            return resp


@app.route('/query')
def query_views():
    # users = db.session.query(Course).all()
    # print(users)
    users = db.session.query(Users).filter(Users.age > 10, Users.id > 2).all()
    # print(users)
    print("名称", "年龄", "邮箱")
    for u in users:
        print(u.username, u.age, u.email)
    return "Query OK~"


@app.route("/query_all")
def query_all():
    print("-------------- 查询所有用户 ----------------------")
    # 查询Users表中所有的数据
    # users = db.session.query(Users).all()
    users = Users.query.all()
    try:
        headers = request.headers
    except Exception:
        pass
    # 将查询结果放到模板中进行显示
    return render_template("02-users_info.html", params=locals())


@app.route("/query_by_id/<int:id>")
def query_by_id(id):
    # user = db.session.query(Users).filter_by(id=id).first()
    user = Users.query.filter(Users.id == id).first()
    headers = request.headers
    return render_template("03-user_selected.html", params=locals())


@app.route("/modify", methods=['GET', 'POST'])
def modify_views():
    if request.method == 'GET':
        id = request.args.get("id")
        user = Users.query.filter_by(id=id).first()
        return render_template("04-modify.html", params=locals())
    else:
        uname = request.form.get('uname')
        uage = request.form['uage']
        uemail = request.form['uemail']
        id = request.form['id']

        # 根据id找出需要修改的记录的对象
        update_user = Users.query.filter_by(id=id).first()

        if db.session.query(Users).filter(Users.username == uname, Users.id != id).all():
            print("用户名重复!")
            return "该用户名已被使用!"
        elif db.session.query(Users).filter(Users.email == uemail, Users.id != id).all():
            print("邮箱重复!")
            return "该邮箱已被使用!"

        else:
            # 修改
            update_user.username = uname
            update_user.age = uage
            update_user.email = uemail

            # 提交修改,当 SQLALCHEMY_COMMIT_ON_TEARDOWN 为 True 的时候将会自动提交
            db.session.add(update_user)

            resp = redirect("/query_all")
            return resp


@app.route("/delete_by_id")
def delete_by_id_views():
    id = request.args.get("id")
    user = Users.query.filter_by(id=id).first()
    db.session.delete(user)
    url = request.headers.get("referer", '/query_all')
    return redirect(url)


# 添加教师
@app.route("/add_teacher", methods=['POST', 'GET'])
def add_teacher_views():
    if request.method == "GET":
        return render_template("05-add_teacher.html")
    else:
        tname = request.form['uname']
        tage = request.form['uage']
        new_teacher = Teacher(tname, tage)

        # if db.session.query(Teacher).filter(Teacher.tname == tname).all():
        #     return "姓名重复"

        # 添加教师
        db.session.add(new_teacher)
        return "成功添加教师 : " + tname + "<br><a href='/add_teacher'>继续添加</a>"


# 教师信息
@app.route("/show_teachers", methods=['GET', 'POST'])
def show_teachers_views():
    if request.method == "GET":
        teachers = Teacher.query.all()
        courses = Course.query.all()
        return render_template("06-show_teachers.html", params=locals())
    else:
        t_id = request.form['t_id']
        c_id = request.form['c_id']
        course_selected = Course.query.filter_by(id=c_id).first()
        teacher = db.session.query(Teacher).filter_by(id=t_id).first()
        teacher.course = course_selected
        return redirect('/show_teachers')


# 添加课程
@app.route("/add_course", methods=['POST', 'GET'])
def add_course_views():
    if request.method == "GET":
        return render_template("06-add_course.html")
    else:
        cname = request.form['cname']
        if Course.query.filter_by(cname=cname).all():
            return "该课程已存在!"
        else:
            new_course = Course(cname)

            # 添加课程
            db.session.add(new_course)
            return "成功添加课程 : " + cname


@app.route("/show_courses")
def show_courses_views():
    courses = Course.query.all()
    return render_template("07-show_courses.html", params=locals())


if __name__ == "__main__":
    app.run(host="10.1.18.44", port=5000, debug=True)
