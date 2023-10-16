import random,os,string
from functools import wraps
from flask import render_template,request,abort,redirect,flash,make_response,url_for,session 


from werkzeug.security import generate_password_hash, check_password_hash

#Local Imports
from pkg import app, csrf
from pkg.models import db, Admin, User, Project, Donation, Payment
from pkg.forms import *


def login_required(f):
   @wraps(f) #This ensures that details(meta data) about the original function f, that is being decorated is still available
   def login_check(*args,**kwargs):
      if session.get("adminuser") !=None:
         return f(*args,**kwargs)
      else:
         flash("Access Denied")
         return redirect('/admin/login')
   return login_check
#To use login_required, place the route decorator over any route that needs authentication


@app.route("/admin/")
@login_required
def admin_page():
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return render_template("admin/login.html")
   else:
      return redirect(url_for('admin_dashboard'))


@app.route("/admin/projects/")
@login_required
def admin_projects():
   if session.get("adminuser") == None or session.get("role")  !='admin':
      return redirect(url_for("admin_login"))
   else:
      
      id = session['adminuser']
      projects = db.session.query(Project).all()
      admin = db.session.query(Admin).get(id)
      return render_template('admin/projects.html',projects=projects,admin=admin) 

@app.route("/admin/login/",methods=["GET","POST"])
def admin_login():
   if request.method =='GET':
      return render_template('admin/login.html')
   else:
      
      #retrieve form data
      username = request.form.get("username")
      pwd = request.form.get("pwd")
      #check if it is in the database
      check = db.session.query(Admin).filter(Admin.admin_username==username,Admin.admin_pwd==pwd).first()
      #if it is in the db, save in session and redirect to dashboard
      if check: #It is indb, save session
         session['adminuser']=check.admin_id
         session['role']='admin'
         return redirect(url_for('admin_dashboard'))
      else: #if not, save message in flash, redirect to login again
         flash('Invalid Login',category='error')
         return redirect(url_for('admin_login'))


@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
   return render_template("admin/dashboard.html")

@app.route("/admin/logout")
def admin_logout():
   if session.get("adminuser") != None:
      session.pop("adminuser",None)
      session.pop("role",None)
      flash("You are logged out",category="info")
      return redirect(url_for("admin_login"))
   else:
      return redirect(url_for('admin_login'))

      
@app.route("/admin/remove_project/<id>/")
@login_required
def remove_project(id):
   projects = db.session.query(Project).get_or_404(id)
   #Lets get the name of the file attached to this project
   filename = projects.project_image
   #First delete the file before deleting the project from db
   if filename != None and filename !='default.png' and os.path.isfile("pkg/static/projects/"+filename):
      os.remove("pkg/static/projects/"+filename)
   db.session.delete(projects)
   db.session.commit()
   flash("The project has been deleted!")
   return redirect(url_for("admin_dashboard"))


@app.route("/admin/viewmore/<id>/",methods=["POST","GET"])
@login_required
def admin_viewmore(id):
   if request.method =="GET":
      project = db.session.query(Project).filter(Project.project_id==id).first_or_404()
      
      status = Project.query.get(id)
      if status:
        payments = Payment.query.filter_by(payment_projectid=id, payment_status='paid').all()

        don = sum(payment.payment_amtpaid for payment in payments)/100
      return render_template("admin/admin_viewmore.html",project=project,don=don)
   else:
      all_don = db.session.query(Donation).filter(Donation.don_projectid).all()
      # don = db.session.query(Donation).filter(Donation.don_amt==all_don).all()

      status = Project.query.get(id)
      

      #Retrieiving the form data
      status.project_status = request.form.get("radio")
      db.session.commit()
      flash("You have successfully changed the status of the project")
      return render_template('admin/dashboard.html' ) 
   
@app.route('/admin/view_users/')
@login_required
def view_users():
   user = db.session.query(User).all()
   return render_template("admin/view_users.html",user=user)

     
@app.route("/admin/delete_user/<id>/")
@login_required
def delete_user(id):
   user = db.session.query(User).get_or_404(id)
   #Lets get the name of the file attached to this project
   filename = user.user_profilepic
   #First delete the file before deleting the project from db
   if filename != None and os.path.isfile("pkg/static/projects/"+filename):
      os.remove("pkg/static/projects/"+filename)
   db.session.delete(user)
   db.session.commit()
   flash("The user has been deleted!")
   return redirect(url_for("view_users"))

@app.route("/admin/home")
def admin_layout():
    return render_template("admin/admin_layout.html")

   


