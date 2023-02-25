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
from models import Event, Skill, User
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

            events = []
            for event in Event.query.filter_by(user_id=user.id).all():
                events.append({"event": event.event, "category": event.category})

            user = {
                "id": user.id,
                "name": user.name,
                "company": user.company,
                "email": user.email,
                "phone": user.phone,
                "skills": skills,
                "events": events,
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

        return f"User '{email}' was successfully registered", 200


class UserResource(Resource):
    # GET /users/:email
    def get(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"User '{email}' does not exist", 400

        skills = []
        for skill in Skill.query.filter_by(user_id=user.id).all():
            skills.append({"skill": skill.skill, "rating": skill.rating})

        events = []
        for event in Event.query.filter_by(user_id=user.id).all():
            events.append({"event": event.event, "category": event.category})

        return (
            {
                "id": user.id,
                "name": user.name,
                "company": user.company,
                "email": user.email,
                "phone": user.phone,
                "skills": skills,
                "events": events,
            },
            200,
        )

    # PUT /users/:email
    def put(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"User '{email}' does not exist", 400

        body = request.get_json()
        if body:
            new_name = body.get("name")
            new_company = body.get("company")
            new_email = body.get("email")
            new_phone = body.get("phone")
            new_skills = body.get("skills")

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

            return f"User '{email}' was successfully updated", 200

        return "Could not update user '{email}'", 400

    # DELETE /users/:email
    def delete(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"User '{email}' does not exist", 400

        db.session.delete(user)
        db.session.commit()

        return f"User '{email}' was successfully deleted", 200


class UserEventsResource(Resource):
    # GET /users/events/:email
    def get(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"User '{email}' does not exist", 400

        events = []
        for event in Event.query.filter_by(user_id=user.id).all():
            events.append({"event": event.event, "category": event.category})

        return events, 200

    # POST /users/events/:email
    def post(self, email):
        user = User.query.filter_by(email=email).first()

        if not user:
            return f"User '{email}' does not exist", 400

        body = request.get_json()
        event = body.get("event")
        category = body.get("category")

        if not (event and category):
            return "Missing fields in body", 400

        # Check if the event is one from the approved list
        if body not in EVENTS:
            return "Invalid event data in body", 400

        # Check to see if the user is already registered to the event
        existing_event = Event.query.filter_by(
            user_id=user.id, event=event, category=category
        ).first()
        if existing_event:
            return f"User '{email}' is already registered to event"

        # Add the new event
        new_event = Event(user_id=user.id, event=event, category=category)
        db.session.add(new_event)
        db.session.commit()

        return f"Successfully registered event to user '{email}'"


class SkillsQuerySchema(Schema):
    min_frequency = fields.Str(required=False)
    max_frequency = fields.Str(required=False)


skills_schema = SkillsQuerySchema()


class SkillsResource(Resource):
    # GET /skills
    def get(self):
        errors = skills_schema.validate(request.args)
        if errors:
            return "Invalid request arguments", 400

        skills = (
            db.session.query(Skill.skill, func.count(Skill.skill).label("count"))
            .group_by(Skill.skill)
            .order_by(func.count(Skill.skill).desc())
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


class EventsQuerySchema(Schema):
    category = fields.Str(required=False)
    min_frequency = fields.Str(required=False)
    max_frequency = fields.Str(required=False)


events_schema = EventsQuerySchema()


class EventsResource(Resource):
    # GET /events
    def get(self):
        errors = events_schema.validate(request.args)
        if errors:
            return "Invalid request arguments", 400

        events = (
            db.session.query(
                Event.event, Event.category, func.count(Event.event).label("count")
            )
            .group_by(Event.event)
            .order_by(func.count(Event.event).desc())
            .all()
        )

        # Filter out events that don't match the specified category (if applicable)
        category = request.args.getlist("category")
        if category:
            events = list(filter(lambda event: (event.category == category[0]), events))

        # Filter out events with a count less than min_frequency (if applicable)
        min_frequency = request.args.getlist("min_frequency")
        if min_frequency:
            events = list(
                filter(lambda event: (event.count >= int(min_frequency[0])), events)
            )

        # Filter out events with a count greater than max_frequency (if applicable)
        max_frequency = request.args.getlist("max_frequency")
        if max_frequency:
            events = list(
                filter(lambda event: (event.count <= int(max_frequency[0])), events)
            )

        return [
            {"event": row[0], "category": row[1], "count": row[2]} for row in events
        ], 200


api.add_resource(UsersResource, "/users")
api.add_resource(UserResource, "/users/<string:email>")
api.add_resource(UserEventsResource, "/users/events/<string:email>")
api.add_resource(SkillsResource, "/skills")
api.add_resource(EventsResource, "/events")

if __name__ == "__main__":
    app.run(debug=True)
