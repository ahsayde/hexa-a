import json, time
from flask import Blueprint, request, render_template, session, redirect
from tools.tools import *
from tools.http import HttpResponse
from authentication.authenticator import *
from client.client import Client

main_pages = Blueprint('main_pages', __name__)

config = read_config()

@main_pages.route("/")
def Index(**kwargs):
    if is_authorized():
        return redirect('/groups', code=302)   
    return render_template('main/index.html')

@main_pages.route("/login", methods=["GET", "POST"])
@logout_required
def LoginPage():
    if request.method == "GET":
        current_url = request.args.get('r', None)
        return render_template('main/login.html', current_url=current_url)

    elif request.method == "POST":
        identifier = request.form['identifier']
        password = request.form['password']
        redirect_url = request.form['current_url']

        if is_valid_credentials(identifier, password):
            authorize_user(identifier=identifier)
            if redirect_url:
                return redirect(redirect_url, code=302)
            else:
                return redirect('/groups', code=302)
        else:
            error = 'Invalid username or password'
            return render_template('main/login.html', error=error)

@main_pages.route("/logout")
@login_required
def LogoutPage(**kwargs):
    logout_user()
    return redirect('/', code=302)


@main_pages.route("/sendresetpassword", methods=['GET', 'POST'])
@logout_required
def SendRestPasswordPage(**kwargs):
    if request.method == 'GET':
        return render_template('main/send_reset_password.html')

    email = request.form.get('email')
    if not email:
        error = 'Please enter your email address'
        return render_template('main/send_reset_password.html', error=error)

    user = User.get(email=email)
    if not user:
        error = 'This email address is not linked to any account'
        return render_template('main/send_reset_password.html', error=error)
        
    token = generate_uuid(length=30)
    secret, salt = hash_password(token)
    timestamp = generate_timestamp()

    resettoken = ResetToken.get(user=user)
    if resettoken:
        resettoken.update(
            salt=salt,
            secret=secret,
            created_at=timestamp
        )
    else:
        resettoken = ResetToken(
            user=user,
            email=email,
            salt=salt,
            secret=secret,
            created_at=timestamp
        )
        resettoken.save()

    subject = "[HEXA-A] Reset account password"
    reset_url = "https://hexa-tool.com/resetpassword?email={}&resettoken={}".format(email, token)
    body = "Please click here {0} to reset your account's password".format(reset_url)

    send_email(
        toaddr=email,
        body=body,
        subject=subject,
        fromaddr=config['emails']['noreply']['addr'],        
        password=config['emails']['noreply']['password'],
    )

    return render_template('main/send_reset_password.html', done=True)

@main_pages.route("/resetpassword", methods=['GET', 'POST'])
@logout_required
def RestPasswordPage(**kwargs):
    
    if request.method == 'GET':
        email = request.args.get('email')
        token = request.args.get('resettoken')
    
    elif request.method == 'POST':
        email = request.form.get('email')
        token = request.form.get('resettoken')
    
    if not (token and email):
        return redirect('/', code=302)

    reset_secret = hash_password(token)[0]
    resettoken_obj = ResetToken.get(email=email)

    if not resettoken_obj:
        return redirect('/', code=302)

    reset_secret = hash_password(token, resettoken_obj.salt)[0]
    if reset_secret != resettoken_obj.secret:
        return render_template('main/reset_password.html', invalid_token=True)

    if (resettoken_obj.created_at + 3600) < time.time():
        return render_template('main/reset_password.html', invalid_token=True)
        
    if request.method == 'GET':
        return render_template('main/reset_password.html', resettoken=token, email=email)

    elif request.method == 'POST':

        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if len(password) < 6:
            error = 'Password length must be at least 6'
            return render_template('main/reset_password.html', resettoken=token, email=email, error=error)
        
        if confirm_password != password:
            error = 'Password does\'t match'
            return render_template('main/reset_password.html', resettoken=token, email=email, error=error)

        secret, salt = hash_password(password) 
        timestamp = generate_timestamp()       
        credentials = Credentials.get(username=resettoken_obj.user.username)
        credentials.update(secret=secret, salt=salt, updated_at=timestamp)
        resettoken_obj.delete()

        return render_template('main/reset_password.html', done=True)

@main_pages.route("/signup", methods=["GET", "POST"])
@logout_required
def Signup():
    if request.method == "GET":
        return render_template('main/signup.html')

    elif request.method == "POST":
        timestamp = generate_timestamp()
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.objects.filter(username=username):
            error = {'username':'username is already used'}
            return render_template('main/signup.html', error=error)

        if User.objects.filter(email=email):
            error = {'email':'email address is already used'}
            return render_template('main/signup.html', error=error)

        if not username.strip() or ' ' in username:
            error = {'username': 'Invalid username'}
            return render_template('main/signup.html', error=error)

        username = username.lower()

        user = User(
            username=username,
            email=email,
            created_at=timestamp)
        
        error = user.check()
        if error:
            return render_template('main/signup.html', error=error)

        secret, salt = hash_password(password)
        credentials = Credentials(
            username=username,
            secret=secret,
            salt=salt,
            email=email,
            created_at=timestamp)

        error = credentials.check()
        if error:
            return render_template('main/signup.html', error=error)

        user.save()
        credentials.save()

        authorize_user(identifier=username)
        return redirect('/dashboard', code=302)