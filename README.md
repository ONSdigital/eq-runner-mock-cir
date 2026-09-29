# eq-runner-mock-cir

A simple FastAPI to mock the CIR service required by eq-runner.


## Pre-requisites

1. [Miniconda](https://docs.conda.io/) - Python and Poetry are installed
into a conda environment from `environment.yml`, so no separate install is needed. The Python
version matches `.python-version`.
2. [Podman](https://podman.io/) - installed from Self Service, if you want to run the app in a container.

## Install Dependencies

Create and activate the conda environment:

```shell
conda env create -f environment.yml
conda activate eq-runner-mock-cir
```

`environment.yml` sets `POETRY_VIRTUALENVS_CREATE=false`, so Poetry installs into the conda
environment instead of creating its own virtualenv. Check it is set:

```shell
echo $POETRY_VIRTUALENVS_CREATE
```

This should print `false`. Then install the dependencies:

```bash
poetry install
```

### Troubleshooting

If `conda env create` fails with `NoWritablePkgsDirError` or a permission error on the notices
cache, run **Repair ownership of user conda directory** in Self Service, then retry.

## Running Locally

To run the FastAPI application locally using `uvicorn`, use the following command:

```bash
make run
```

The application will be accessible at `http://localhost:5004`.

## Run with Podman

Make sure the Podman machine is started:

```shell
podman machine start
```

Build the image:

```shell
podman build -t eq-runner-mock-cir .
```

Run the container:

```shell
podman run -d -p 5004:5004 eq-runner-mock-cir
```

The FastAPI app will be available at `http://localhost:5004`.

For convenience when typing container commands by hand, you can add an alias to your shell profile:

```shell
alias docker='podman'
```

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
