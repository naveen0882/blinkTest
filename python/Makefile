run:
	python3 kayles/app.py

test:
	-coverage run --source=. -m unittest discover
	coverage report --omit=*test_*.py,setup.py,kayles/config.py,kayles/app.py
	@rm .coverage

install:
	@echo "Installing: make sure you sourced the virtualenv"
	pip3 install -r requirements.txt
	python3 setup.py develop

clean:
	find . | grep -E "(__pycache__|\.pyc$$)" | xargs rm -rf
	python3 setup.py develop --uninstall
	rm -rf *.egg-info
	rm -rf ../env/

help:
	@echo "run - run the local app server"
	@echo "test - run the tests"
	@echo "install - installs the dependencies and app (source the virtualenv first)"
	@echo "clean - removes all generated files"
