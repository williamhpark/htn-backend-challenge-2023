# Hack the North Backend Challenge 2023 - William Park

## Setting up and running the server

### Docker setup

1. Ensure that Docker is installed on your system
2. Pull my docker image by running `docker pull williamhpark/htn-be-challenge`
3. Verify that the `williamhpark/htn-be-challenge` image was successfully pulled using the `docker images` command
4. Run `docker run -p 8000:5000 williamhpark/htn-be-challenge`. The local server should run on `http://127.0.0.1:8000`

### Manual setup

1. If you have issues using the Docker image, pull the code from this Github repo onto your local system
2. Navigate to this project's root directory
3. Ensure that Python 3 is installed on your system (I'm using Python 3.8)
4. Create a Python virtual environment: `python -m venv htn-venv`
5. Activate the virtual environment: `source htn-venv/bin/activate`
6. Install the required dependencies: `pip install -r requirements.txt`
7. Create a `db` directory: `mkdir db`
8. Run `flask run`. The local server should run on `http://127.0.0.1:5000`

If you run into any issues while setting up or running the server, please let me know.

## Choice of technology

- The server was built as a REST API using Flask-RESTful in Python. I chose to use Flask-RESTful because I had experience building APIs with it before, and its simplicity allows you to create REST APIs quickly. I like the REST architectural style because it's a widely adopted architecture in the industry, it supports multiple different data formats (e.g. JSON, XML, YAML), and the server is independent from the client allowing for high scalability and flexibility

- The provided user profile JSON data was populated into a SQLite database. The user data has a fixed schema, so a relational database seemed like the appropriate choice. I chose SQLite because it's the easiest to setup, as mentioned in the challenge description, and I used the SQLAlchemy ORM to interact with the database for ease of development and cleaner code compared to using raw queries

- The server was containerized using Docker

- The automated unit tests were written using the pytest framework

## API routes

- `GET /users`: Retrieve all users\*
- `POST /users`: Create (or register) a new user

- `GET /users/:email`: Retrieve data on a user specified by email\*
- `PUT /users/:email`: Update the data for a user specified by email\*
- `DELETE /users/:email`: Delete the data for a user specified by email

- `GET /users/events/:email`: Retrieve a list of the events the user specified by email attended
- `POST /users/events/:email`: Add to the list of events attended by a user specified by email (i.e. "scan" them in)

- `GET /skills?min_frequency=min_frequency&max_frequency=max_frequency`: Retrieve the number of users that have each skill, with optional min_frequency and max_frequency filters\*

- `GET /events?category=category&min_frequency=min_frequency&max_frequency=max_frequency`: Retrieve a list of all the events at the hackathon with a count of users who attended, with optional category, min_frequency, and max_frequency filters

## Testing instructions

In the project's root directory, run `pytest`. All automated unit tests should run.

## Notes on development

- I set up the required API endpoints requested in the challenge description (marked with a **\*** in the API routes descriptions), then added a few endpoints providing additional CRUD functionality to the `/users` and `/users/:email` routes as well as a few endpoints related to events at the hackathon that users "scan" into

- I decided to use the user's email as the piece of data that identifies a single user, since each user's email should be unique. I noticed that there were one or two instances of reused emails in the `HTN_2023_BE_Challenge_Data.json` file, and while populating the database I thought it made most sense to skip the user instances with reused emails

- While you can update the user's skills using the `PUT /users/:email` endpoint, you cannot update the events that they've attended (or in other words, "scan" a user into an event). I thought it made sense to handle this in a separate endpoint, `POST /users/events/:email`

- The `GET /skills` and `GET /events` API endpoints accomplish similar goals, where they return a list of the skills that the hackathon attendees have or the events that they've scanned into with an associated count. I decided to return the results in descending order of popularity, and this data could provide interesting insight to attendees and could also help organizers decide which workshops and events to host in future hackathons

- I decided to create a fake set list of the events that attendees could participate in and reject any requests to register to events outside of this list to imitate how this endpoint would likely be set up for an actual hackathon

- Basic error checking was included for all API routes. For instance, if any API request is made for a specific user and that user does not exist, or a client tries to update a user's email to one already associated with another existing user, then a `400 Bad Request` error should be returned

## Potential improvements

- Encode and decode the email params passed in the API URLs. Generally, symbols like `@` should not be passed in URLs since they don't fit a format that can be transmitted over the internet. So when passing an email in the URL, it should be encoded (e.g. `test@gmail.com` -> `test%40gmail.com`) then decoded when used in the code
- Secure the API endpoints. Since the API deals with somewhat sensitive user data, in a real application we would want only authenticated users to be able to make requests to the API. This authentication could be implemented using JSON Web Tokens
- Return more intentional response status codes rather than just 200 or 400
- Use a more powerful database, such as MySQL or PostgreSQL. One of the major limitations of SQLite is the fact that it has little support for concurrency, which is important for applications such as this one where we could expect multiple requests and changes to the database occuring at the same time
- Abstract some of the code better. For example, checking if a user with a specific email exists and returning a `400 Bad Request` if they don't exist was implemented several times throughout the API. Abstracting this, as well as some other code, into helper functions would make the code cleaner and more reusable
- More thorough argument/body validation. For example, ensuring that the phone number passed when creating a new user matches the expected format of a valid phone number
- Connect the server to a frontend so it's easier for a client to interact with the API endpoints
