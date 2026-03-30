from flask import Blueprint
 #always import routes here so even the decorators are registered
bp = Blueprint("auth", __name__) #this is a module package always __init__.py should be the entery point 
#auth is the blueprint name and it acts as an endpoint 
#only if your template folder is inside this auth or folder then include its name otherwise just leave it from app.auth import routes
from app.auth import routes
#always import this line after difining blueprint 