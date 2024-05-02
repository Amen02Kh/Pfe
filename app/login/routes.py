from flask import render_template, redirect, url_for, flash, request
from app.login import bp
from app.login.forms import LoginForm
from app.models.users import User
from werkzeug.security import check_password_hash
from flask_login import login_user

@bp.route('/',methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and check_password_hash(user.password_hash, form.password.data):
            
            login_user(user)
            return redirect(url_for('main.index'))  # Redirect to dashboard or appropriate page
        else:
            flash('Invalid username or password', 'error')
    return render_template('login/index.html', form=form)