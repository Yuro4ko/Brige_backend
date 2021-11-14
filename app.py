from src import app

if __name__ == '__main__':
    print("Binding...")
    app.run(debug=False, host='0.0.0.0')