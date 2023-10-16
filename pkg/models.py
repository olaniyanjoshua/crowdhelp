from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()


class User(db.Model):
   user_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
   user_name = db.Column(db.String(45), nullable=False, unique=True)
   user_fname = db.Column(db.String(45), nullable=False, unique=False)
   user_lname = db.Column(db.String(45), nullable=False, unique=False)
   user_email = db.Column(db.String(45), nullable=False, unique=True)
   user_phoneno = db.Column(db.String(45), nullable=False, unique=False)
   user_password = db.Column(db.String(200), nullable=False)
   user_profilepic = db.Column(db.String(120), nullable=False)
   user_datereg = db.Column(db.DateTime(), default=datetime.utcnow)
   #set relationship
   user_projects=db.relationship("Project",back_populates='projectsby')   

   
   
class Sponsor(db.Model):
   sponsor_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
   sponsor_userid = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False)
   sponsor_projectid = db.Column(db.Integer, db.ForeignKey('project.project_id'),nullable=False) 
   sponsor_amtdonated = db.Column(db.Float, nullable=False)   
   sponsor_donationdate = db.Column(db.DateTime(), default=datetime.utcnow)

  
class Project(db.Model):
   project_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
   project_name = db.Column(db.String(100), nullable=False)   
   project_description = db.Column(db.Text(), nullable=False)   
   project_amt = db.Column(db.Float, nullable=False)  
   project_datecreated = db.Column(db.DateTime(), default=datetime.utcnow)
   project_image=db.Column(db.String(120),nullable=True) 
   project_userid = db.Column(db.Integer, db.ForeignKey('user.user_id'),nullable=False) 
   project_status =db.Column(db.Enum('published','unpublished'),nullable=False, server_default=("unpublished")) 
    #set relationship
   projectsby=db.relationship("User",back_populates='user_projects')   
   
  

   
class Donation(db.Model):
   don_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
   don_amt = db.Column(db.Float, nullable=False)  
   don_userid = db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable=True)
   don_projectid = db.Column(db.Integer,db.ForeignKey("project.project_id"),nullable=True)
   don_date = db.Column(db.DateTime(), default=datetime.utcnow)

class Payment(db.Model):
   payment_id = db.Column(db.Integer, autoincrement=True,primary_key=True)
   payment_donationid = db.Column(db.Integer,db.ForeignKey("donation.don_id"),nullable=True)
   payment_projectid = db.Column(db.Integer,db.ForeignKey("project.project_id"),nullable=True)
   payment_userid = db.Column(db.Integer,db.ForeignKey("user.user_id"),nullable=True)
   payment_amtpaid = db.Column(db.Float,nullable=False)
   payment_datepaid = db.Column(db.DateTime(), default=datetime.utcnow)
   payment_status =db.Column(db.Enum('pending','failed','paid'),nullable=False, server_default=("pending")) 
   payment_refno = db.Column(db.String(20),nullable=False)
   payment_paygate_response = db.Column(db.Text())

   
class Admin(db.Model):
    admin_id=db.Column(db.Integer, autoincrement=True,primary_key=True)
    admin_username=db.Column(db.String(20),nullable=True)
    admin_pwd=db.Column(db.String(200),nullable=True)
    
