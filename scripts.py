import json

from sqlalchemy.exc import IntegrityError

from api import app, db, User, Skill


def init_db():
    with app.app_context():
        # Create all database tables
        db.create_all()

        # Populate database with JSON fake user profile data

        users_json = json.load(open("HTN_2023_BE_Challenge_Data.json"))

        user_columns = ["name", "company", "email", "phone"]
        skill_columns = ["skill", "rating"]
        for user in users_json:
            # Add the user record to the database
            user_values = {}
            for column in user_columns:
                user_values[column] = str(dict(user).get(column))

            new_user = User(**user_values)
            db.session.add(new_user)

            # If a user does not satisfy the unique email constraint, skip
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
                continue

            # Add the user's skill records to the database
            for skill in dict(user).get("skills"):
                skill_values = {}
                for column in skill_columns:
                    skill_values[column] = str(skill.get(column))

                skill_values["user_id"] = new_user.id
                new_skill = Skill(**skill_values)
                db.session.add(new_skill)
                db.session.commit()
