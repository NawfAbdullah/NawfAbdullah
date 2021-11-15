import os
import smtplib
import psycopg2
from flask import Flask,render_template,url_for,request,redirect,flash,abort
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from datetime import datetime,date
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.utils import secure_filename
from flask import send_from_directory
from forms import CreateNewProject,RegistrationForm,LoginForm,CommentForm
from flask_bootstrap import Bootstrap
from flask_ckeditor import CKEditor
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_gravatar import Gravatar
import random




UPLOAD_FOLDER = 'static/user/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
ckeditor = CKEditor(app)
Bootstrap(app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL","sqlite:///portfolio.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)

gravatar = Gravatar(app,
 size=100, 
 rating='g', 
 default='retro', 
 force_default=False, 
 force_lower=False, 
 use_ssl=False, 
 base_url=None)


class MyProjects(db.Model):
    __tablename__ = "my_projects"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250),unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    is_blog = db.Column(db.Boolean(),nullable=False)
    date = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment",back_populates="post")


class User(UserMixin, db.Model):
    __tablename__ = "users" 
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
    comment = relationship("Comment",back_populates="commenter")

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer,primary_key=True)
    text = db.Column(db.Text,nullable=False)
    commenter_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    commenter = relationship('User',back_populates="comment")
    post_id = db.Column(db.Integer,db.ForeignKey('my_projects.id'))
    post    = relationship('MyProjects',back_populates='comments')


#db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_only(f):
    @wraps(f)
    def decorated_function(*args,**kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args,*kwargs)
    return decorated_function



@app.route('/')
def home():
    showcase = []
    projects = MyProjects.query.all()
    print(projects)
    #while len(showcase)<=4 and len(showcase>=3):
    for i in range(6):
        if projects!=[]:
            x = random.choice(projects)
            if not x.is_blog:
                showcase.append(x)
                projects.remove(x)
        if len(showcase) == 4:
            break

    today = datetime.now()
    return render_template('index.html',projects=showcase,year=today.year)


@app.route('/contact-me',methods=['GET','POST'])
def contact_me():
    if request.method == 'POST':
        MY_EMAIL = "hungrypy6@gmail.com"
        MY_PASSWORD = "klugnawf"
        if request.method == "POST":
            data = request.form
            with smtplib.SMTP('smtp.gmail.com',587) as connection:
                connection.starttls()
                connection.login(MY_EMAIL,MY_PASSWORD)
                connection.sendmail(from_addr=MY_EMAIL,to_addrs=MY_EMAIL,msg=f''' f"Subject:New Message\n\nName: {data['name']}\nEmail: {data['email']}\nPhone: {data['phone']}\nMessage:{data['message']}"''')
            return "<h1>Successfully sent your message</h1>"
    return render_template('contact.html')




def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads', methods=['GET', 'POST'])
@login_required
@admin_only
def upload_file():
	form = CreateNewProject()
	if form.validate_on_submit():
		#if 'file' not in request.files:
		#	print('This guy')
		#	return redirect(request.url)
		file = form.img.data
		print(file)
		if file.filename == '':
			print('empty1')
			return redirect(request.url)

		if file and allowed_file(file.filename):
			print('success')
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			
			new_project = MyProjects(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=url_for('static',filename=f"user/uploads/{filename}"),
            is_blog=form.is_blog.data,
            date=date.today().strftime("%B %d, %Y")
		        )
			db.session.add(new_project)
			db.session.commit()
			return redirect(url_for('projects'))

	return render_template('secret.html',form=form)

@app.route('/projects')
def projects():
    all_projects = MyProjects.query.all()
    return render_template('projects.html',projects=all_projects)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        name = form.name.data
        if User.query.filter_by(email = email).first():
            flash("This email already exist")
            return redirect(url_for('login'))
        else:
            hash_and_salted_password = generate_password_hash(
                password,
                method='pbkdf2:sha256',
                salt_length=8
            )
            new_user = User(email = email,password=hash_and_salted_password,name=name)
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect('/')
    return render_template("register.html",form = form,logged_in=current_user.is_authenticated)


@app.route('/login',methods = ['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password,form.password.data):
                flash("You've Successfully logged in")
                login_user(user)
                return redirect('/')
            else:
                flash("Incorrect Username or password")
        else:
            flash("This Email doesn't Exist")


    return render_template("login.html",form = form ,logged_in=current_user.is_authenticated)

@app.route('/projects/<int:id>',methods=["GET","POST"])
def discrete(id):
    project = MyProjects.query.get(id)
    all_project_comments = Comment.query.all()
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or reqister to comment")
            return redirect(url_for("login"))
        new_comment = Comment(
            text = form.commentbox.data,
            commenter = current_user,
            post = project
            )
        db.session.add(new_comment)
        db.session.commit()
        return render_template("project-at.html", project=project,form=form,current_user=current_user,comments=all_project_comments)


    return render_template("project-at.html", project=project,form=form,current_user=current_user,comments=all_project_comments)

@app.route("/blogs")
def BlogsPage():
    all_projects = MyProjects.query.all()
    blog_posts = [blogs for blogs in all_projects if blogs.is_blog]
    return render_template('blog.html',all_posts=blog_posts)


@app.route("/blogs/<int:post_id>",methods = ["GET",'POST'])
def show_post(post_id):
    requested_post = MyProjects.query.get(post_id)
    all_blog_comments = Comment.query.all()
    form = CommentForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or reqister to comment")
            return redirect(url_for("login"))
        new_comment = Comment(
            text = form.commentbox.data,
            commenter = current_user,
            post =requested_post
            )
        db.session.add(new_comment)
        db.session.commit()


    return render_template("project-at.html", project=requested_post,form=form,current_user=current_user,comments=all_blog_comments)

@login_required
@admin_only
@app.route("/delete/<post_id>")
def delete_post(post_id):
    post_to_delete = MyProjects.query.get(post_id)
    print(post_to_delete)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
	app.run(debug=True)


#{{url_for('project', id=project.id)}}