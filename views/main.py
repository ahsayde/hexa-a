import json
from flask import Blueprint, request, render_template, session, redirect
from tools.tools import *
from tools.http import HttpResponse
from authentication.authenticator import *
from client.client import Client

main_pages = Blueprint('main_pages', __name__)

@main_pages.route("/")
def Index(**kwargs):
    if is_authorized():
        return render_template('user/dashboard.html')    
    return render_template('main/index.html')

@main_pages.route("/login", methods=["GET", "POST"])
@logout_required
def LoginPage():
    if request.method == "GET":
        return render_template('main/login.html')

    elif request.method == "POST":
        identifier = request.form['identifier']
        password = request.form['password']

        if is_valid_credentials(identifier, password):
            authorize_user(identifier=identifier)
            return redirect('/dashboard', code=302)
        else:
            error = 'Invalid username or password'
            return render_template('main/login.html', error=error)

@main_pages.route("/logout")
@login_required
def LogoutPage(**kwargs):
    logout_user()
    return redirect('/', code=302)


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