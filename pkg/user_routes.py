import random, os, string, json, requests
from functools import wraps
from tkinter import PAGES
from flask import render_template,request,abort,redirect,flash,make_response,url_for,session ,jsonify

from werkzeug.security import generate_password_hash, check_password_hash

#Local Imports
from pkg import app, csrf
from pkg.models import db, User, Project, Payment, Donation, Sponsor
from pkg.forms import *


def generate_string(howmany): #cal this function 
   x = random.sample(string.ascii_lowercase,howmany)
   return ''.join(x)

def generate_string2(howmany):
   x = random.sample(string.digits,howmany)
   return ''.join(x)

def login_required(f):
   @wraps(f) #This ensures that details(meta data) about the original function f, that is being decorated is still available
   def login_check(*args,**kwargs):
      if session.get("user") !=None:
         return f(*args,**kwargs)
      else:
         flash("Access Denied")
         return redirect('/login')
   return login_check
#To use login_required, place the route decorator over any route that needs authentication


@app.route("/donate/<id>",methods=["POST","GET"])
@login_required
def donation(id):
   donform = DonForm()
   if request.method =="GET":
      uid = session.get('user')
      userdeets = db.session.query(User).get(uid)
      #deets = db.session.query(User).get(session['user'])
      return render_template("user/donation.html",donform=donform,userdeets=userdeets)
   else:
      if donform.validate_on_submit():
         #retrieve form data
         amt = float(donform.amt.data) * 100
         projectid = db.session.query(Project).get(id)
         #generate a traansaction reference number
         ref = 'CH' +str(generate_string2(8)) + 'LP'
         #insert into database
         uid = session.get('user')
         if session.get("user") !="":
            session['user'] = uid
         else:
            session['user'] = 0

         donation = Donation(don_amt=amt,don_userid=session['user'],don_projectid=projectid.project_id)
         db.session.add(donation)
         db.session.commit()

         payment = Payment(payment_donationid=donation.don_id,payment_amtpaid=amt,payment_status='pending',payment_refno=ref,payment_projectid=projectid.project_id,payment_userid=session['user'])
         db.session.add(payment)
         db.session.commit()

         sponsor = Sponsor(sponsor_userid=uid,sponsor_projectid=projectid.project_id,sponsor_amtdonated=amt)
         db.session.add(sponsor)
         db.session.commit()

         #save the reference number in session
         session['crhelp'] = ref
        
         #redirect to a confirmation page
         return redirect("/confirm_donation")
      else:
         if session.get("user") !="":
            session['user'] = session['user']
         else:
            session['user'] = 0
            deets = db.session.query(User).get(session['user'])
            return render_template("user/donation.html",donform=donform,userdeets=userdeets)
         

@app.route("/confirm_donation/",methods=["POST","GET"])
@login_required
def confirm_donation():
   """We want to display the details of the transaction saved from the previous page"""
   id = session.get('user')
   userdeets = db.session.query(User).get(id)
   # deets = db.session.query(User).get(session['user'])
   if session.get('crhelp') == None: #means they are visiting directly
      flash("Please complete this form", category="error")
      return redirect("/donate")
   else:
      payment_deets = Payment.query.filter(Payment.payment_refno==session['crhelp']).first()
      #donation_deets = Payment.query.filter(Payment.payment_userid==session['crhelp']).first()
      return render_template("user/donation_confirmation.html",payment_deets=payment_deets,userdeets=userdeets)
   

@app.route("/initialize/paystack")
@login_required
def initialize_paystack():
   userdeets  = User.query.get(session['user'])
   #transaction details
   refno = session.get('crhelp')
   transaction_deets = db.session.query(Payment).filter(Payment.payment_refno==refno).first()
   #make a curl request to the paystack endpoint
   #!/bin/sh
   url="https://api.paystack.co/transaction/initialize"
   headers = {"Content-Type": "application/json","Authorization": "Bearer sk_test_68cfdaa437bb717f7133bad25f539fc6fe9cfea8"}
   data={"email": userdeets.user_email, "amount": transaction_deets.payment_amtpaid, "reference":refno }
   response = requests.post(url,headers=headers,data=json.dumps(data))
   #extract json from the response coming from paystack
   rspjon = response.json()
   #return rspjon
   if rspjon['status'] ==True:
      redirectURL = rspjon['data']['authorization_url']
      return redirect(redirectURL) #paystack payment page will load
   else:
      flash("Please complete the form again")
      return redirect('/donate')


@app.route("/landing")   
@login_required
def landing_page():
   refno = session.get('crhelp')
   transaction_deets = db.session.query(Payment).filter(Payment.payment_refno==refno).first()
   url="https://api.paystack.co/transaction/verify/" +transaction_deets.payment_refno
   headers = {"Content-Type": "application/json","Authorization": "Bearer sk_test_68cfdaa437bb717f7133bad25f539fc6fe9cfea8"}
   response = requests.get(url,headers=headers)
   rspjon = json.loads(response.text)
   if rspjon['status'] ==True:
      paystatus = rspjon['data']['gateway_response']
      transaction_deets.payment_status = 'Paid'
      db.session.commit()
      return redirect('/dashboard') 
   else:
      flash('payment failed')
      return redirect('/reports')
   

@app.route("/createproject/",methods=["POST","GET"])
@login_required
def create_project():
   id = session.get('user')
   userdeets =db.session.query(User).get(id)
   proj = ProjForm()
   if request.method =="GET":
      return render_template('create_project.html',proj=proj,userdeets=userdeets,pagename="Create A Project")
   else:
      if proj.validate_on_submit():
         projname = request.form.get("projname")
         projdesc = request.form.get("projdesc")
         projamt = request.form.get("projamt")
         

         pix = request.files.get("projimage")#check if file was selected for upload
         if pix.filename !="":
         #let thefilename remain the same on the database
      
           name,ext = os.path.splitext(pix.filename)
           if ext.lower() in ['.jpg','.png','.jpeg']:
              newfilename = generate_string(10) + ext
              pix.save("pkg/static/projects/"+ newfilename)
              pix = newfilename



         p = Project(project_userid=id,project_name=projname,project_description=projdesc,project_amt=projamt,project_image=pix)
         #filename = pix.filename
         #pix.save("pkg/static/projects/"+newfilename)
         userdeets.project_image= newfilename
         db.session.add(p)
         db.session.commit()
         flash("Your project has been successfully created")
         return redirect(url_for('create_project'))
      else:
         return render_template('user/create_project.html',proj=proj,userdeets=userdeets,pagename="Create A Project")


@app.route('/checkusername/',methods=["POST","GET"])
def checkusername():
      username = request.form.get('fullname')
      query = db.session.query(User).filter(User.user_name==username).first()
      if query:
         flash("The username has been taken")
         return ""
      else:
         flash("The username has been accepted")
         return "" 


@app.route('/checkemail/',methods=["POST","GET"])
def checkemail():
      email = request.form.get('fullname')
      query = db.session.query(User).filter(User.user_email==email).first()
      if query:
         flash("The email has been taken")
         return ""
      else:
         flash("The email has been accepted")
         return "" 


@app.route("/projects/", methods=["POST","GET"])
def projects():
   id = session.get('user')
   userdeets = User.query.get(id)
   projects = db.session.query(Project).all()
   return render_template('user/projects.html',projects=projects,userdeets=userdeets)


@app.route('/search/', methods=['POST','GET'])
def search():
    search = request.form.get('query')
    if search:
        # Perform a database search or any other search logic
        results = Project.query.filter(Project.project_name.like(f"%{search}%")|Project.project_description.like(f"%{search}%")).all()
        if results:
           flash("Record found")
        else:
           flash("Record not found")
        return render_template("user/search.html",results=results)
       



@app.route("/viewmore/<id>")
def view_more(id):
   pid = session.get('user')
   userdeets = User.query.get(pid)
   project = Project.query.get_or_404(id)
   status = Project.query.get(id)
   if status:
       payments = db.session.query(Payment).filter(Payment.payment_projectid == id, Payment.payment_status == 'paid').all()
        #payments = Payment.query.filter_by(payment_projectid=id, payment_status='paid').all()

       don = sum(payment.payment_amtpaid for payment in payments)/100
   projects = db.session.query(Project).filter(Project.project_name).all()
   return render_template("user/viewmore.html",project=project,userdeets=userdeets,projects=projects,don=don)

@app.route("/myprojects/")
def myprojects():
   id = session['user']
   userdeets = User.query.get(id)
   user = db.session.query(User).get(id)
   return render_template("user/myprojects.html",user=user,userdeets=userdeets)

@app.route("/changedp/",methods=["POST","GET"])
@login_required
def changedp():
   id = session.get("user")
   userdeets = db.session.query(User).get(id)
   dpform = DpForm()
   if request.method =="GET":
      return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)
   else:
      if dpform.validate_on_submit():
         pix = request.files.get('dp')
         filename = pix.filename
         pix.save(app.config['USER_PROFILE_PATH']+filename)
         userdeets.user_profilepic = filename
         db.session.commit()
         flash("Profile picture updated")
         return redirect(url_for('dashboard'))
      else:
         return render_template("user/changedp.html",dpform=dpform,userdeets=userdeets)

@app.route("/",methods=["POST","GET"])
def home():
   return render_template("user/index.html")

@app.route("/signup/",methods=["POST","GET"])
def signup():
   sign = RegForm()
   if request.method == "GET":
      return render_template("user/signup.html",sign=sign)
   else:
         #retrieve file
         if sign.validate_on_submit():
            allowed = ['jpg','png']
            fileobj = request.files['profile']
            filename = fileobj.filename
            newname = "default.png" #default cover
            if filename =='': #No file was uploaded
               flash("Book cover not included",category='error')
            else: #file was selected # To make sure it is random
               newname =str(int(random.random()*1000000000))+filename
               pieces = filename.split('.')
               ext = pieces[-1]#.lower()
               if ext.lower() in allowed:
                  fileobj.save("pkg/static/profiles/" + newname)
               else:
                  flash("File extension not allowed, file was not upoaded",category='error')

         
               username = request.form.get("username")
               email = request.form.get("email")
               pwd = request.form.get("pwd")
               fname = request.form.get("fname")
               lname = request.form.get("lname")
               phoneno = request.form.get("phoneno")
               #profile = request.form.get("profile")
               hashed_pwd = generate_password_hash(pwd)
               u = User(user_name=username,user_fname=fname,user_lname=lname,user_email=email,user_phoneno=phoneno,user_password=hashed_pwd,user_profilepic=newname)
               db.session.add(u)
               db.session.commit()
               flash("An account has been created for you. Please login.")
               return redirect('/login')
         else:
            return render_template("user/signup.html",sign=sign)


@app.route("/login/",methods=["POST","GET"])
def login():
   if request.method =="GET":
      return  render_template("user/login.html")
   else:
       username = request.form.get('username')
       pwd = request.form.get('pwd')
       deets = db.session.query(User).filter(User.user_name==username).first()
       if deets !=None:
         hashed_pwd = deets.user_password
         if check_password_hash(hashed_pwd,pwd) == True:
            session['user'] = deets.user_id
            return redirect("/dashboard")
         else:
            flash("Invalid Credentials, try again")
            return redirect("/login")
       else:
            flash("Invalid Credentials, try again")
            return redirect("/login")
      
       
      

@app.route("/dashboard/")
def dashboard():
   if session.get('user') != None:
      id = session.get('user')
      userdeets = User.query.get(id)
   # within dashboard display the persons name
      flash("You need to login to access this page")
      return render_template("user/dashboard.html",userdeets=userdeets)
   else:
      flash("You must be logged in to view this page")
      return redirect("/login")

   


@app.route("/logout")
def logout():
   if session.get("user") != None:
      session.pop("user",None)
   return redirect("/")


@app.after_request
def after_request(response):
   #To solve the problem
   response.headers["Cache-Control"]="no-cache, no-store, must-revalidate"
   return response


   
@app.route("/changepassword/",methods=["POST","GET"])
def change_password():
   id = session.get('user')
   userdeets = User.query.get(id)
   if request.method =="GET":
      return render_template("user/changepassword.html",userdeets=userdeets)
   else:
       username = request.form.get('username')
       pwd = request.form.get('pwd')
       deets = db.session.query(User).filter(User.user_name==username).first()
       if deets !=None:
         hashed_pwd = deets.user_password
         if check_password_hash(hashed_pwd,pwd) == True:
            newpwd = request.form.get('pwd2')
            hashed_newpwd = generate_password_hash(newpwd)
            deets.user_password = hashed_newpwd
            db.session.commit()
            if session.get("user") != None:
               session.pop("user",None)
            flash("You have successfully changed your password, please log in to continue")
            return redirect('/login')

         else:
            flash("Invalid Credentials, try again")
            return redirect("/changepassword")

#@app.route("/index/") These functions are controller
@app.errorhandler(404)
def page_not_found(error):
   return render_template("user/error404.html",error=error),404

@app.errorhandler(500)
def server_error(error):
   return render_template("user/error500.html",error=error),500

