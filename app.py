from flask import Flask, request, jsonify, render_template
import os
import time
import random

app = Flask(__name__)

memory = []
MAX_MEMORY = 100


def remember(state, action, reward=None):
    memory.append({
        "state": state,
        "action": action,
        "reward": reward,
        "time": int(time.time())
    })

    if len(memory) > MAX_MEMORY:
        del memory[:-MAX_MEMORY]


def choose_action(state):
    """
    Game AI Agent
    รับ state ของเกม แล้วเลือก action
    """

    if not isinstance(state, dict):
        state = {}

    # ข้อมูลพื้นฐานจากเกม
    health = float(state.get("health", 100))
    enemy_visible = bool(state.get("enemy_visible", False))
    enemy_distance = float(state.get("enemy_distance", 999))
    can_attack = bool(state.get("can_attack", False))
    can_jump = bool(state.get("can_jump", True))

    # หลักการตัดสินใจเบื้องต้น
    if health <= 20:
        action = {
            "type": "retreat"
        }

    elif enemy_visible and can_attack and enemy_distance <= 10:
        action = {
            "type": "attack"
        }

    elif enemy_visible and enemy_distance <= 30:
        action = {
            "type": "move",
            "direction": "backward"
        }

    elif can_jump and random.random() < 0.15:
        action = {
            "type": "jump"
        }

    else:
        action = {
            "type": "move",
            "direction": "forward"
        }

    remember(state, action)

    return action


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/generate", methods=["GET", "POST"])
def api_generate():

    if request.method == "GET":
        return jsonify({
            "success": True,
            "status": "online",
            "agent": "Game Agent",
            "endpoint": "/api/generate",
            "method": "POST"
        })

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "JSON body required"
        }), 400

    state = data.get("state", data)

    try:
        action = choose_action(state)

        return jsonify({
            "success": True,
            "action": action
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route("/api/reward", methods=["POST"])
def api_reward():

    data = request.get_json(silent=True) or {}

    reward = data.get("reward", 0)

    try:
        reward = float(reward)
    except (TypeError, ValueError):
        reward = 0

    if memory:
        memory[-1]["reward"] = reward

    return jsonify({
        "success": True,
        "reward": reward
    })


@app.route("/api/memory", methods=["GET"])
def api_memory():
    return jsonify({
        "memory": memory
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "online",
        "agent": "Game Agent",
        "model": "app.py"
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
