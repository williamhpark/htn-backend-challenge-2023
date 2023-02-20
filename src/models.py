from api import db


class User(db.Model):
    __tablename__ = "user"

    # Database fields
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    phone = db.Column(db.String(80), nullable=False)
    skills = db.relationship(
        "Skill", backref="user", cascade="all, delete", passive_deletes=True
    )

    def __repr__(self):
        return f"User('{self.id}', '{self.name}', '{self.company}', '{self.email}', '{self.phone}', '{self.skills}')"


class Skill(db.Model):
    __tablename__ = "skill"

    # Database fields
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"))
    skill = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Skill('{self.id}', '{self.user_id}', '{self.skill}', '{self.rating}')"
