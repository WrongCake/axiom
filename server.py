from flask import Flask, request
import logging

app = Flask(__name__)

@app.route('/')
def home():
    app.logger.info('Home endpoint accessed.')
    return "I'm alive"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(host='0.0.0.0', port=8080)
