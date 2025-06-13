# Weather API

## Setup

First create `.env` file from `.env.dist` with:
```bash
cat .env.dist >> .env
```

**Don't forget fill the WEATHER_API_X_TOKEN**

You can generate token with this command:

```bash
openssl rand -base64 32
```

## Docker

You can start the project with docker using this command:

```bash
docker-compose up --build
```

If you want to develop in docker with autoreload and exposed ports add `-f deploy/docker-compose.dev.yml` to your docker command.
Like this:

```bash
docker-compose -f docker-compose.yml -f deploy/docker-compose.dev.yml --project-directory . up --build
```

## Swagger
http://localhost:8000/api/docs/
