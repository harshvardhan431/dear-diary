import logging
import os
from logging.handlers import RotatingFileHandler #it creates a file that auto resets its size 

def setup_logger(app): #this connect our app to logging system
    if not os.path.exists('logs'):
        os.mkdir('logs') #creates a file which consist of logging data

    if app.logger.hasHandlers(): #if file is already created then it clears the file 
        app.logger.handlers.clear()

    file_handler = RotatingFileHandler(
        'logs/app.log', maxBytes=10240, backupCount=5
    )#changes the file size and prevents disk overload

    file_handler.setLevel(logging.INFO) #this sets the level this means the file stores info,warning,error

    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)s | %(name)s | %(message)s'
    )
     #each log will look like 2026-03-22 12:00:00 | INFO | app | User logged in
    file_handler.setFormatter(formatter)

    error_handler = RotatingFileHandler(
        'logs/error.log', maxBytes=10240, backupCount=5
    )#separate file only stores the error

    error_handler.setLevel(logging.ERROR)#error,critical are stored here
    error_handler.setFormatter(formatter)#same format is applied for this file too

    app.logger.addHandler(file_handler)#this addhangler help the flask to know where to save and how to save them
    app.logger.addHandler(error_handler)

    app.logger.setLevel(logging.INFO) #globally minimum level is info