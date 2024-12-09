import asyncio
import hashlib
import threading

from flask import Flask, jsonify, render_template, request

from food_co2_estimator import async_estimator

app = Flask(__name__)

results = {}  # Temporary storage for results


def hash_input(input_data):
    """Generate a short hash from input data."""
    return hashlib.md5(input_data.encode()).hexdigest()


def run_in_thread(func, input_data):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    hashed_input = hash_input(input_data)
    try:
        result = loop.run_until_complete(func(input_data, verbose=True))
        results[hashed_input] = result
    except Exception as exc_info:
        print(str(exc_info))
        results[hashed_input] = "Something went wrong. :-( Please try again."
    finally:
        loop.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate")
def calculate():
    input_data = request.args.get("input_data")
    if not input_data:
        return jsonify(status="No input provided"), 400

    threading.Thread(target=run_in_thread, args=(async_estimator, input_data)).start()

    hashed_input = hash_input(input_data)
    return (
        jsonify(status="Processing", input_data=input_data, hashed_input=hashed_input),
        202,
    )  # Return 202 Accepted status


@app.route("/results/<hashed_input>")
def get_results(hashed_input):
    result = results.get(hashed_input, None)
    if result is not None:
        return jsonify(status="Completed", result=result), 200
    else:
        return jsonify(status="Processing", input_data=hashed_input), 202


if __name__ == "__main__":
    app.run(debug=True, port=8000)
