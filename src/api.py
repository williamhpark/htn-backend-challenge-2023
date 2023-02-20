import os

from marshmallow import Schema, fields
from sqlalchemy import func

from flask import Flask, request
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy


# Initialize the Flask app
app = Flask(__name__)

# Configure the SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(
    basedir, "db/", "database.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Create the SQLAlchemy extension
db = SQLAlchemy(app)

# Import the User database model
from models import User, Skill
from scripts import init_db

# Populate the SQLite database with the data from HTN_2023_BE_Challenge_Data.json
init_db()


# Initialize the REST API
api = Api(app)


class UsersResource(Resource):
    # GET /users
    def get(self):
        users = []
        for user in User.query.all():
            skills = []
            for skill in Skill.query.filter_by(user_id=user.id).all():
                skills.append({"skill": skill.skill, "rating": skill.rating})

            user = {
                "id": user.id,
                "name": user.name,
                "company": user.company,
                "email": user.email,
                "phone": user.phone,
                "skills": skills,
            }
            users.append(user)

        return users, 200


class UserResource(Resource):
    # GET /users/<email>
    def get(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"The user '{email}' does not exist", 404

        skills = []
        for skill in Skill.query.filter_by(user_id=user.id).all():
            skills.append({"skill": skill.skill, "rating": skill.rating})

        return (
            {
                "id": user.id,
                "name": user.name,
                "company": user.company,
                "email": user.email,
                "phone": user.phone,
                "skills": skills,
            },
            200,
        )

    # PUT /users/<email>
    def put(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"The user '{email}' does not exist", 404

        json_body = request.get_json()
        if json_body:
            if json_body.get("name"):
                user.name = json_body.get("name")
            if json_body.get("company"):
                user.company = json_body.get("company")
            if json_body.get("email"):
                user.email = json_body.get("email")
            if json_body.get("phone"):
                user.phone = json_body.get("phone")
            if json_body.get("skills"):
                for skill in json_body.get("skills"):
                    if not skill.get("rating"):
                        return "No rating provided", 400

                    existing_skill = Skill.query.filter_by(
                        user_id=user.id, skill=skill.get("skill")
                    ).first()
                    if existing_skill:
                        existing_skill.rating = skill.get("rating")
                    else:
                        new_skill = Skill(
                            user_id=user.id,
                            skill=skill.get("skill"),
                            rating=skill.get("rating"),
                        )
                        db.session.add(new_skill)

            db.session.commit()

            return f"Successfully updated user '{email}'", 200

        return "Could not update user '{email}'", 400


class SkillsQuerySchema(Schema):
    min_frequency = fields.Str(required=False)
    max_frequency = fields.Str(required=False)


schema = SkillsQuerySchema()


class SkillsResource(Resource):
    # GET /skills
    def get(self):
        skills = (
            db.session.query(Skill.skill, func.count(Skill.skill).label("count"))
            .group_by(Skill.skill)
            .all()
        )

        # Filter out skills with a count less than min_frequency (if applicable)
        min_frequency = request.args.getlist("min_frequency")
        if min_frequency:
            skills = list(
                filter(lambda skill: (skill.count >= int(min_frequency[0])), skills)
            )

        # Filter out skills with a count greater than max_frequency (if applicable)
        max_frequency = request.args.getlist("max_frequency")
        if max_frequency:
            skills = list(
                filter(lambda skill: (skill.count <= int(max_frequency[0])), skills)
            )

        return [{"skill": row[0], "count": row[1]} for row in skills], 200


api.add_resource(UsersResource, "/users")
api.add_resource(UserResource, "/users/<string:email>")
api.add_resource(SkillsResource, "/skills")

if __name__ == "__main__":
    app.run(debug=True)
