from flask import render_template,request, redirect, url_for, flash
from app.panel import bp
from app.extensions import db
from app.models.users import User
from app.models.report import Report
from werkzeug.security import generate_password_hash
from flask_login import login_required, current_user

@bp.route('/')
@login_required
def index():
    if not current_user.is_admin:
        
        return render_template('unauthorized/index.html')
    users = User.query.all()

    return render_template('panel/index.html',users=users)


@bp.route('/add_user', methods=['GET', 'POST'])
@login_required
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
    
        # Hash the password
        hashed_password = generate_password_hash(password)
    
        # Create a new user instance with the hashed password
        new_user = User(username=username, email=email, password_hash=hashed_password)
    
        # Add the new user to the database
        db.session.add(new_user)
        try:
            db.session.commit()
            flash('User added successfully!')
        except Exception as e:
            db.session.rollback()
            flash('Error adding user: ' + str(e))

        return redirect(url_for('panel.index'))  # Ensure 'panel.index' is the correct endpoint for redirection
    return render_template('panel/index.html')


@bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    try:
        db.session.commit()
        flash('User deleted successfully!')
    except Exception as e:
        flash('Error deleting user: ' + str(e))
    return redirect(url_for('panel.index'))


@bp.route('/update_user', methods=['POST'])
@login_required
def update_user():

    if request.method == 'POST':
        user_id = request.form['user_id']
        new_username = request.form['username']
        new_email = request.form['email']
        new_password = request.form.get('password')  

        # Find the existing user
        user = User.query.get(user_id)
        if not user:
            
            return redirect(url_for('panel.index'))

        # Update user details
        old_username=user.username
        user.username = new_username
        user.email = new_email
        Report.query.filter_by(analyst=old_username).update({'analyst': new_username})
        # Update the password if a new one is provided
        if new_password:
            user.password_hash = generate_password_hash(new_password)

        # Attempt to commit changes to the database
        try:
            db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            

        return redirect(url_for('panel.index'))

    return redirect(url_for('panel.index'))