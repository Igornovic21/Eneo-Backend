
# ENEO Backend

Instructions for easy handling of the ENEO Backend

## Docker Installation

Clone the project

```bash
  git clone https://github.com/GeOsmFamily/Eneo_backend.git
```

Go to the project directory

```bash
  cd Eneo_backend
```

Add `.env` file at the root of the folder

```bash
  cp .env.example .env
```

Add `.env.db` file inside the `.docker` folder

```bash
  cp .docker/.env.example.db .docker./env.db
```

Place the itinary.geojson file inside the fixtures folder

```bash
  cp /path_to_my/itinary_file.geojson /fixtures/itineraire.geojson
```

### Environment Variables

To run this project, you will need to add the following environment variables to your `.env` and `.env.db` file

`POSTGRES_DB`

`POSTGRES_USER`

`POSTGRES_PASSWORD`

`POSTGRES_HOST`

`POSTGRES_PORT` (recommended value in paranthesis)

`DATA_UPLOAD_MAX_MEMORY_SIZE` (recommended value in paranthesis)

`DATA_UPLOAD_MAX_NUMBER_FIELDS` (recommended value in paranthesis)

### Running Scripts

Start the docker containers of the project

```bash
  docker compose up -d
```