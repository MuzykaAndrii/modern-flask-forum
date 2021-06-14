from flask import Blueprint, render_template, request, url_for, flash, redirect, abort
from app.forms import RegistrationForm, LoginForm
from app.models import User
from flask_login import current_user, login_user, logout_user
from app import url_serializer, mail
from flask_mail import Message
from itsdangerous import SignatureExpired, BadSignature

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/')
def redirect_auth():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():

        # gather data from form
        nickname = form.nickname.data
        email = form.email.data
        password = form.password.data

        # save data to database
        user = User(nickname, email, password)
        user.save()

        token = url_serializer.dumps(email, salt='email-confirm')
        link = url_for('auth.confirm_email', token=token, _external=True)

        msg = Message('Confirm email', recipients=[email])
        msg.body = 'Hello, {} your confirmation link: {}'.format(nickname, link)
        mail.send(msg)

        flash(f'Account created for {nickname}, please check email messages to continue registration', 'warning')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

@auth.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        email = url_serializer.loads(token, salt='email-confirm', max_age=86400)
        user = User.query.filter_by(email=email).first_or_404()
        user.email_confirmed = True
        user.save()
    except SignatureExpired:
        return render_template('alerts/token_expired')
    except BadSignature:
        return abort(404)
    flash('email address successfully confirmed, now you can log in into your account', 'success')
    return redirect(url_for('auth.login'))

####### LOGIN
@auth.route('/login', methods=['GET', 'POST'])
def login():
    #redirect if loginned
    if current_user.is_authenticated:
        flash('You have been already logged in', category='warning')
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():

        #gather data
        email = form.email.data
        password = form.password.data
        result = User.query.filter_by(email=email).first()

        #check if user exist and password hash is equals
        if result is None or not result.check_password(password):
            flash('Login unsuccessfull. Please check nickname and password', category='warning')
            return redirect(url_for('auth.login'))

        # check if user not banned
        elif result.is_banned == True:
            return render_template('alerts/banned.html', reason=result.ban_reason)
        
        # check if email confirmed
        elif result.email_confirmed != True:
            return render_template('alerts/not_confirmed.html', email=result.email)

        else:
            flash(f'{result.nickname}, you have been logged in!', category='success')
            login_user(result, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('index'))
            
    return render_template('auth/login.html', form=form, title='Login')

######### LOGOUT
@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('index'))