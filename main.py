from app import create_app
print("Server starting...")
app=create_app()
print("Server starting")
if __name__=="__main__": #this checks that the files is executed when it runs directly thorugh the server not when imported
    app.run(debug=True)
    
    #only run the server when this file is executed directyly not imported