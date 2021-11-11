from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,BooleanField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, URL,Email
from flask_ckeditor import CKEditorField

##WTForm
class CreateNewProject(FlaskForm):
    title 	 = StringField("Project Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    img      = FileField(validators=[DataRequired()])
    body 	 = CKEditorField("Blog Content", validators=[DataRequired()])
    is_blog  = BooleanField("Is it a Blog?")
    submit 	 = SubmitField("Submit Post")

class RegistrationForm(FlaskForm):
    email    = StringField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    name     = StringField("Name",validators=[DataRequired()])
    submit   = SubmitField("Sign up")
    

class LoginForm(FlaskForm):
	email    = StringField("Email",validators=[DataRequired(),Email()])
	password = PasswordField("Password",validators=[DataRequired()])
	submit   = SubmitField("Let me in!")

class CommentForm(FlaskForm):
	commentbox = CKEditorField('Comment',validators=[DataRequired()])
	submit     = SubmitField("Comment") 