# QuafelWeb

QuafelWeb is a web application to visualize and manage data from various
quantum computing simulators with the help of [Quafel](https://github.com/cirKITers/Quafel).

## Set up and run the project

### Project Dependencies
- [Python 3.11.9](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/)
- [Docker](https://docs.docker.com/get-docker/)

### Finish Setting Up
After installing the dependencies and cloning the repository, 
run the following command in the root of the project to install the 
python dependencies and finish setting up:

```bash
poetry install
```

### Run the project
To run the project, the following commands must be executed:

- This will start the database and the simulated hardware profile:
```bash
docker-compose up -d
```

- this will update the database schema:
```bash
poetry run python quafelweb/manage.py migrate
```

- This will start the web application:
```bash
poetry run python quafelweb/manage.py runserver
```

### Additional information
- The web application can be accessed at `http://localhost:8000/`
- The simulated hardware-profile is available via ssh at `localhost:2222` 
with the credentials `user:password`
