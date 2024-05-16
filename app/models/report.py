from app.extensions import db


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    analyst = db.Column(db.String(100), db.ForeignKey('user.username'))
    pdf_data = db.Column(db.Text)
    ana = db.relationship('User', backref=db.backref('reports', lazy=True))
    def __repr__(self):
        return f'<Report {self.name}>'
