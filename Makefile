DC = docker-compose
EXEC = docker exec -it
LOGS = docker logs
ENV = --env-file .env
DOCKER_COMPOSE_FILE = docker-compose.yaml
MARKET_CONTAINER = market

.PHONY: app
app:
	${DC} -f ${DOCKER_COMPOSE_FILE} ${ENV} up --build -d

.PHONY: app-up
app-up:
	${DC} -f ${DOCKER_COMPOSE_FILE} ${ENV} up -d

.PHONY: app-down
app-down:
	${DC} -f ${DOCKER_COMPOSE_FILE} down

.PHONY: market-shell
market-shell:
	${EXEC} ${MARKET_CONTAINER} bash

.PHONY: market-logs
market-logs:
	${LOGS} ${MARKET_CONTAINER} -f

.PHONY: market-alembic-revision
market-alembic-revision:
	${EXEC} ${MARKET_CONTAINER} alembic revision --autogenerate -m "update"

.PHONY: market-alembic-upgrade
market-alembic-upgrade:
	${EXEC} ${MARKET_CONTAINER} alembic upgrade head

