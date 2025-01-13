# Payment Portal

This project is a payment portal application with a backend built using FastAPI/MongoDB and a frontend built using Angular.

## Backend

### Development Server

To start the backend development server, run:

```bash
uvicorn app.main:app --reload
```

The backend server will start at [http://localhost:8000](http://localhost:8000).

### Dependencies

The backend dependencies are managed using Poetry. To install the dependencies, run:

```bash
poetry install
```

## Frontend

To start the frontend development server, run:

```bash
ng serve
```

Once the server is running, open your browser and navigate to [http://localhost:4200/](http://localhost:4200/). The application will automatically reload whenever you modify any of the source files.

### Building

To build the project, run:

```bash
ng build
```

This will compile your project and store the build artifacts in the `dist/` directory. By default, the production build optimizes your application for performance and speed.

### Running Unit Tests

To execute unit tests with the Karma test runner, use the following command:

```bash
ng test
```

### Running End-to-End Tests

For end-to-end (e2e) testing, run:

```bash
ng e2e
```

Angular CLI does not come with an end-to-end testing framework by default. You can choose one that suits your needs.

### Additional Resources

For more information on using the Angular CLI, including detailed command references, visit the [Angular CLI Overview and Command Reference](https://angular.io/cli) page.

### Environment Configuration

The environment configuration for the frontend can be found in the `environment.ts` file. Update the `apiUrl` to point to your backend server.

## Docker

To build and run the project using Docker, use the provided `Dockerfile` and `docker-compose.yml` files.

### Building Docker Images

To build the Docker images, run:

```bash
docker-compose build
```

### Running Docker Containers

To start the Docker containers, run:

```bash
docker-compose up
```

The backend server will be available at [http://localhost:8000](http://localhost:8000) and the frontend at [http://localhost:4200](http://localhost:4200).