from flask import Flask, render_template
import redis
import os

app = Flask(__name__)

redis_host = os.getenv("VISITOR_REDIS_HOST", "localhost")
redis_port = int(os.getenv("VISITOR_REDIS_PORT", 6379))

redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

@app.route("/")
def index():
    count = redis_client.incr("visitor_count")
    return render_template("index.html", count=count)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
