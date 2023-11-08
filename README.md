# eq-runner-mock-cir

A simple FastAPI to mock the CIR service required by eq-runner.


## Pre-requisites

1. Python installed using [Pyenv](https://github.com/pyenv/pyenv). Version is specified in `.python-version` file.
2. [Poetry Package Manager](https://python-poetry.org/)

## Install Dependencies

To install dependencies using poetry, run the following command:

```bash
poetry install
```

## Running Locally

To run the FastAPI application locally using `uvicorn`, use the following command:

```bash
make run
```

The application will be accessible at `http://localhost:5004`.

## Docker

You can also containerize the application using Docker.

1. Build the Docker image:

```bash
docker build -t eq-runner-mock-cir .
```

1. Run the Docker container:

```bash
docker run -d -p 5004:5004 eq-runner-mock-cir
```

The FastAPI app will be available at `http://localhost:5004`.

## Development

### Code Formatting

To format the code using black, run the following command:

```bash
make format
```

### Code Linting

To lint the code using black, run the following command:

```bash
make lint
```

### Load schemas

To load in the schemas from `eq-questionnaire-schemas` and the test schemas from `eq-questionnaire-runner` run the following command:

```bash
make load-schemas
```

### Testing

To run the unit tests, first load schemas as the test require them, then run the following command:

```bash
make test
```
