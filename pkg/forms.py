from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, SubmitField, PasswordField, FileField, TextAreaField, FloatField, FormField
from wtforms.validators import Email, DataRequired, EqualTo, Length

class RegForm(FlaskForm):
   username = StringField("Username",validators=[DataRequired(message="The Username is a must"),Length(min=4,message="Your username is too short")])
   #lname = StringField("Lastname",validators=[Length(min=5)])
   fname = StringField("First Name",validators=[DataRequired(message="The firstname is a must"),Length(min=4,message="Your firstname is too short")])
   lname = StringField("Last Name",validators=[DataRequired(message="The lastname is a must"),Length(min=4,message="Your lastname is too short")])
   #lname = StringField("Lastname",validators=[Length(min=5)])
   #lname = StringField("Lastname",validators=[Length(min=5)])
   email = StringField("Email",validators=[Email(message="Invalid Email Format"),DataRequired(message="Email must be supplied"),Length(min=5,message="Email is too short")])
   phoneno = FloatField("Phone Number",validators=[DataRequired(message="Enter your phone number")])
   pwd = PasswordField("Enter Password",validators=[DataRequired()])
   conpwd = PasswordField("Confirm Password",validators=[EqualTo('pwd',message="let the two password match")])
   profile = FileField("Choose a profile picture",validators=[DataRequired(message="You must upload an image to continue"),FileRequired(),FileAllowed(['jpg','png','jpeg'])])
   btnsubmit = SubmitField("Signup")

class ProjForm(FlaskForm):
   projname = StringField("Project Name",validators=[DataRequired(message="The Project must have a name"),Length(min=7,message="Your project is too short")])
   projdesc = TextAreaField("Project Description",validators=[DataRequired(message="The Project can't be without a description"),Length(min=10,message="Your project description is too short, you need to describe your project explicitly.")])
   projamt = FloatField("Project Amount",validators=[DataRequired(message="You need to specify the amount required for treatment")])
   projimage = FileField("Choose an image for the project",validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
   projbtn = SubmitField("Create Your Project")

   
class DpForm(FlaskForm):
   dp = FileField("Upload a Profile Picture",validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'])])
   btnupload = SubmitField("Upload Picture")

class ProfileForm(FlaskForm):
   username = StringField("Username",validators=[DataRequired(message="The username is a must")])
   btnsubmit = SubmitField("Update Profile")

class DonForm(FlaskForm):
  fullname = StringField("Fullname",validators=[DataRequired(message="The fullname is a must")])
  email = StringField("Email",validators=[Email(message="Invalid Email Format"),DataRequired(message="Email must be supplied"),Length(min=5,message="Email is too short")])
  amt = FloatField("Specify Amount",validators=[DataRequired()])
  btnsubmit = SubmitField("Submit")

class SearchForm(FlaskForm):
   search = StringField("Search a project by it's name",validators=[DataRequired(message="Search can't be empty")])
   btnsubmit = SubmitField("Search")
   form = FormField("Search by project name")

   
