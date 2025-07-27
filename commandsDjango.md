//Install django
pip install django

// Create a new Django project
django-admin startproject projectname . # . is the current directory

// Create a new Django app
python manage.py startapp appname

// Run the server
python manage.py runserver

// Create a superuser
python manage.py createsuperuser

// Create a new migration
python manage.py makemigrations


// Apply migrations
python manage.py migrate

// Run the tests
python manage.py test

// Check vulnerabilities in the project
python manage.py check --deploy


// Para hacer los archivos de traduccion
python manage.py makemessages -all

//Compilar los archivos de traduccion
python manage.py compilemessages


// Force migrate
python manage.py migrate --run-syncdb


// Delete migrations
Get-ChildItem -Recurse -Filter "*.pyc" -Path .\ -Include "*/migrations/*.pyc" | Remove-Item


Get-ChildItem -Recurse -Path . -Filter "*.py" -Exclude "__init__.py" | Where-Object { $_.FullName -match '\\migrations\\' } | Remove-Item


//Colect static
python manage.py collectstatic --noinput
