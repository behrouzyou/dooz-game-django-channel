# Dooz Game — Django

A Django project for a Dooz (Tic-Tac-Toe-style) game. The current view renders a game template and passes a game ID into the page.

## Stack
- Python
- Django
- Django templates

## Run locally
Create and activate a Python virtual environment, install the dependencies used by the project, and run:

```bash
python manage.py migrate
python manage.py runserver
```

The repository's current view establishes the game page entry point. Review the game app's routing, templates, and any real-time/channel-layer configuration for the complete interaction flow.
