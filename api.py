import json
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

# Set list of events at the Hacakthon
EVENTS = json.load(open("./mock_data/events_data.json"))


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

    # POST /users
    def post(self):
        body = request.get_json()

        name = body.get("name")
        company = body.get("company")
        email = body.get("email")
        phone = body.get("phone")

        # Check for all required body fields
        if not (name and company and email and phone):
            return "Missing fields in body", 400

        # Check if the user is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return f"User '{email}' already exists", 400

        # Add the new user to the database
        user = User(name=name, company=company, email=email, phone=phone)
        db.session.add(user)
        db.session.commit()

        # Add the skills to the skills database table
        skills = body.get("skills")
        if skills:
            for skill in skills:
                # If data is missing from the skill, skip
                if not (skill.get("skill") and skill.get("rating")):
                    return "Invalid skill entry provided", 400

                new_skill = Skill(
                    user_id=user.id,
                    skill=skill.get("skill"),
                    rating=skill.get("rating"),
                )
                db.session.add(new_skill)

        db.session.commit()

        return f"User {email} was successfully registered", 200


class UserResource(Resource):
    # GET /users/:email
    def get(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"The user '{email}' does not exist", 400

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

    # PUT /users/:email
    def put(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"The user '{email}' does not exist", 400

        json_body = request.get_json()
        if json_body:
            new_name = json_body.get("name")
            new_company = json_body.get("company")
            new_email = json_body.get("email")
            new_phone = json_body.get("phone")
            new_skills = json_body.get("skills")

            if new_email:
                existing_user = User.query.filter_by(email=new_email).first()
                if existing_user:
                    return (
                        f"Update failed, user with email '{new_email}' already exists",
                        400,
                    )

                user.email = new_email
            if new_name:
                user.name = new_name
            if new_company:
                user.company = new_company
            if new_phone:
                user.phone = new_phone
            if new_skills:
                # Purge all existing skills for the user
                existing_skills = Skill.query.filter_by(user_id=user.id).all()
                for skill in existing_skills:
                    db.session.delete(skill)

                db.session.commit()

                # Add the new skills the database
                for skill in new_skills:
                    if not (skill.get("skill") and skill.get("rating")):
                        return "Invalid skill entry provided", 400

                    new_skill = Skill(
                        user_id=user.id,
                        skill=skill.get("skill"),
                        rating=skill.get("rating"),
                    )
                    db.session.add(new_skill)

            db.session.commit()

            return f"Successfully updated user '{email}'", 200

        return "Could not update user '{email}'", 400

    # DELETE /users/:email
    def delete(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"The user '{email}' does not exist", 404

        db.session.delete(user)
        db.session.commit()

        return f"Successfully deleted user '{email}'", 200


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
