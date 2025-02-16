create_app:
	python3 manage.py startapp apps

run:
	python3 manage.py runserver localhost:8000

create_user:
	python3 manage.py createsuperuser


mig:
	python3 manage.py makemigrations
	python3 manage.py migrate