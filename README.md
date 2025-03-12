# TimeZone Identifier

## Overview
Simple API to get the timezone of a given location and to list all the timezones.

## API Endpoint
- **GET** `/timezones`
  - **Description**: Get all available timezones
  - **Query Params**:
    - **Description**: When provided, the API will return the timezone of the given location
    - `lat`: Latitude of the location
    - `lon`: Longitude of the location
  - **Response**:
    - **200**: The timezone of the given location or all available timezones
    - **400**: Invalid parameters
    - **500**: Internal server error

## Technologies
Pre-requisity: `Docker` for running the containerized application and its dependencies locally.
The following technologies are used:
- Python 3.11
- Django (Python web framework)
- Django Rest Framework (REST API framework for Django)
- PostgreSQL (Database)
- PostGIS (Spatial extension for PostgreSQL)
- [Geospatial Libraries](https://docs.djangoproject.com/en/5.1/ref/contrib/gis/install/geolibs/) - GEOS, PROJ, GDAL

## How to run
1. Clone the repository

2. Create a `.env` file in the root directory of the project with the generated values for keys given in `.env.dist` file

3. Run the following command to start the server
    ```bash
    $ docker compose up --build -d
    ```
4. The server will be running on http://localhost:8000

5. To get all available timezones, make a GET request to http://localhost:8000/timezones

6. To get the timezone of a given location, make a GET request to http://localhost:8000/timezones?lat={latitude}&lon={longtitude}

## Methodology
### Timezone identification

#### Inhabited areas
Timezone identification is based on the spatial data source available at http://efele.net/maps/tz/world/. The data is alligned with the borders of the countries in polygon representation. The data is in the form of shapefile which is mapped to GeoDjango model and imported into the PostGIS database. The timezone of the location is identified by checking predefined radius of the location. This approach is used because it is reusable for the puropose of identifying timezone in the territorial waters.

#### Territorial Waters
As of [NOAA](https://www.noaa.gov/maritime-zones-and-boundaries#territorial), the territorial waters of a country extend upto 12 nautical miles from the baseline. For both these purposes, the `Distance` function of PostGIS is used to check if the location is within 12 nautical miles of the border of the country. If the location is within the territorial waters of a country or in the country, the timezone of the country is returned. This method is not 100% accurate but it is good enough for most of the cases. 

#### Uninhabitted areas
The spatial data source includes areas considered to be uninhabited, therefore without a meaningful timezone. Identification of the timezone in these arease are the same as the identification of the timezone in the international waters. For the purpose of identifying the timezone in the internatial waters, the location is checked against generated table of timezones boundaries. The boundaries are meridians 15° apart, except UTC+12 and UTC-12 which are 7.5° apart. The timezone within the boundary is returned as the timezone of the location. This method is used for the cases locating timezone in international waters and of a uninhabited area (including Antarctica).

## All timezones
The list of all timezones is generated from the spatial data source by grouping the timezones by name and returning the timezone name. For completeness of the data the list of all timezones includes all generated timezones in the form of timezone offset (UTC+12).

### Data sources
- [Shapefile of the timezones](http://efele.net/maps/tz/world/tz_world.zip)
- Generated table of timezones boundaries
Both data sources are imported into the PostGIS database on the startup of the application using the initial migration.

### Limitations
- checkup of source data
- internal waters - big US lakes, Black Sea, Caspian Sea, etc.
- Antarctica - timezone should depend on the base
- distance calculations in PostGIS
- timezone on the border of the areas and on the border of the meridians


## Development
### Useful commands
<!-- TODO: Add tests for the API and edit this-->
1. Start the server
```bash
$ docker compose up --build -d
```
2. Run the tests in running container
```bash
$ docker exec -it django_app python3 manage.py test
```
3. Access the running container
```bash
$ docker compose exec -it django_app bash
```


### Python static code analysis - `ruff`
- [ruff](https://docs.astral.sh/ruff/) linter and formatter can be manually triggered using
```bash
$ ruff check          # Lint files in the current directory.
$ ruff check --fix    # Lint files in the current directory and fix any fixable errors.
$ ruff format         # Format all files in the current directory.
```
- basic configuration is introduced in `pyproject.toml`

### TODO Before production
- Setup production settings
- Setup CI/CD pipeline
- Setup monitoring, logging and alerting
- Setup security measures
- Setup production database and infrastructure with backups
- Add more tests to cover more scenarios
- Add caching to reduce the response time
- Execute load tests
- Add rate limiting to prevent abuse
- Add authentication to secure the API
- Improve timezone identification using more data
- Add more features like getting the timezone of a given address

## Existing solutions
- [Google Maps Time Zone API](https://developers.google.com/maps/documentation/timezone/overview)
- [timezonefinder](https://github.com/jannikmi/timezonefinder) python library
- [tzfpy](https://github.com/ringsaturn/tzfpy) python library written in Rust
