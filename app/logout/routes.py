from flask import redirect, url_for, flash
from app.logout import bp
from flask_login import login_required, current_user ,logout_user


@bp.route('/',methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login.login'))