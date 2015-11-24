from apiflask import db
from apiflask.models import Student

stu = Student.query.filter(Student.stuid=='2013302480033').first()
db.session.delete(stu)
db.session.commit()
print Student.query.all()
