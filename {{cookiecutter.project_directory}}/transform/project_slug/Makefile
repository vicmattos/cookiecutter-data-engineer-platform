.PHONY: default all run test load-env

default: run

all: run test

run: load-env
	@dbt run --profiles-dir .

test: load-env
	@dbt test --profiles-dir .

load-env:
	$(source .env)
