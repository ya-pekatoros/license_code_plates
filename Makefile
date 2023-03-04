#development variables
install:
		poetry install
		
build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --force-reinstall --user dist/*.whl

start:
		poetry run python license_plates_stat/scheduler.py
		
show-active-ports:
		sudo lsof -i -P -n | grep LISTEN
# kill -9 processid - force comand to kill process

.PHONY: install
