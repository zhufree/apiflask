from apiflask import db


class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    stuid = db.Column(db.String(64), unique = True)
    stupwd = db.Column(db.String(64))

    def __repr__(self):
        return '<Student %r>' % (self.stuid)
