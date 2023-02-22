# Hack the North Backend Challenge 2023 - William Park

## Technology

The server was built as a REST API using Flask-Restful with Python.

The JSON data was populated into a SQLite database.

The server was containerized using Docker.

## Setting up and running the server

If you run into any issues while setting up or running the server, please let me know.

## API routes

- `GET /users`: Retrieve all users
- `POST /users`: Create (or register) a new user

- `GET /users/:email`: Retrieve data on a user specified by email
- `PUT /users/:email`: Update the data for a user specified by email
- `DELETE /users/:email`: Delete the data for a user specified by email

- `GET /users/events/:email`: Retrieve a list of the events the user specified by email attended
- `POST /users/events/:email`: Add to the list of events attended by a user specified by email

- `GET /skills?min_frequency=min_frequency&max_frequency=max_frequency`: Retrieve the number of users that have each skill, with optional min_frequency and max_frequency filters

- `GET /events?category=category&min_frequency=min_frequency&max_frequency=max_frequency`: Retrieve a list of all the events at the Hackathon as well as a count of users who attended each event, with optional category, min_frequency, and max_frequency filters

## Potential improvements

- Build the endpoint suggested in the challenge instructions for scanning the hacker badges
- More intentional return codes rather than just 200 or 400
- More powerful database, such as MySQL or PostgreSQL
