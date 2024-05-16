from flask import render_template,send_file,flash,redirect,url_for
from app.history import bp
from flask_login import login_required, current_user
from app.extensions import db
from app.models.report import Report
from config import Config
import io
import os
import pdfkit

@bp.route('/',methods=['GET'])
@login_required
def index():
    reps = Report.query.all()
    return render_template('history/index.html',reps=reps)

@bp.route('/download_rep/<int:rep_id>',methods=['POST'])
@login_required
def download_rep(rep_id):
     report = Report.query.get(rep_id)
     report_folder = Config.REPORT_FOLDER
     filename = f'{report.name}.pdf'
     save_path = os.path.join(report_folder, filename)
     
     pdfkit.from_string(report.pdf_data, save_path)
     if report and report.pdf_data:
        return send_file(
            save_path,
            as_attachment=True,
        )
     else:
        return "Report not found", 404

@bp.route('/delete_rep/<int:rep_id>',methods=['POST'])
@login_required
def delete_rep(rep_id):
    report = Report.query.get(rep_id)
    db.session.delete(report)
    try:
        db.session.commit()
        flash('User deleted successfully!')
    except Exception as e:
        flash('Error deleting user: ' + str(e))
    return redirect(url_for('history.index'))
