"""Flask entry point for the AI News Agent.

Boot with: flask --app app.main:app run --reload (from modules/api).
The app is built by app.factory.create_app.
"""

from app.factory import create_app

app = create_app()
