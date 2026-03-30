from app import create_app
print("Server starting...")
app=create_app()
print("Server starting")
if __name__=="__main__":
    app.run(debug=True)
    print("Server starting...")