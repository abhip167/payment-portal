FROM python:3.12 as requirements-stage

WORKDIR /tmp
RUN pip install poetry==1.6.0
COPY ./pyproject.toml ./poetry.lock* /tmp/
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with=dev

FROM python:3.12

WORKDIR /code
COPY --from=requirements-stage /tmp/requirements.txt .
RUN pip install --no-cache-dir --upgrade -r ./requirements.txt
COPY . .

ENTRYPOINT ["sh", "./scripts/launch_prod.sh"]