from flask import Flask, request, jsonify, render_template
import os
import time

app = Flask(__name__)

memory = []

MAX_MEMORY = 50


def remember(role, content):
    memory.append({
        "role": role,
        "content": content,
        "time": int(time.time())
    })

    if len(memory) > MAX_MEMORY:
        del memory[:-MAX_MEMORY]


def generate_ai(prompt):
    """
    จุดนี้จะเป็นสมอง AI ของเรา
    ตอนนี้ยังไม่ผูกกับโมเดลใด เพื่อไม่ล็อกระบบผิดตัว
    """

    remember("user", prompt)

    # TODO:
    # เชื่อมโมเดล AI ตรงนี้

    response = {
        "text": "AI backend พร้อมแล้ว แต่ยังไม่ได้เชื่อมโมเดล AI",
        "status": "model_not_connected"
    }

    remember("assistant", response["text"])

    return response


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "JSON body required"
        }), 400

    prompt = data.get("prompt")

    if not prompt or not isinstance(prompt, str):
        return jsonify({
            "error": "prompt is required"
        }), 400

    prompt = prompt.strip()

    if not prompt:
        return jsonify({
            "error": "prompt is empty"
        }), 400

    try:
        result = generate_ai(prompt)

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/memory", methods=["GET"])
def api_memory():
    return jsonify({
        "memory": memory
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "service": "AI Agent API"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
