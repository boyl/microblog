"""
**********************************************************************
app/
    errors/                             <-- blueprint package
        __init__.py                     <-- blueprint creation
        handlers.py                     <-- error handlers
    templates/
        errors/                         <-- error templates
            404.html
            500.html
    __init__.py                         <-- blueprint registration
**********************************************************************
"""

from flask import Blueprint


bp = Blueprint('errors', __name__)


from app.errors import handlers
