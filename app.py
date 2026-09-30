from flask import Flask, request, jsonify, render_template
import math
import os

app = Flask(__name__)

# ============================================================
# CONFIG
# ============================================================

# ขนาดของแต่ละช่องในโลกเกม
GRID_SIZE = 10.0

# ความเร็วการเคลื่อนที่โดยประมาณ
MOVE_SPEED = 10.0

# จำนวนช่องสูงสุดที่ใช้คำนวณเส้นทาง
MAX_PATH_CELLS = 10000


# ============================================================
# GRID
# ============================================================

def world_to_grid(x, y, z):
    return {
        "x": math.floor(x / GRID_SIZE),
        "y": math.floor(y / GRID_SIZE),
        "z": math.floor(z / GRID_SIZE)
    }


def grid_to_world(gx, gy, gz):
    return {
        "x": gx * GRID_SIZE,
        "y": gy * GRID_SIZE,
        "z": gz * GRID_SIZE
    }


# ============================================================
# DISTANCE
# ============================================================

def distance_3d(a, b):
    dx = b["x"] - a["x"]
    dy = b["y"] - a["y"]
    dz = b["z"] - a["z"]

    return math.sqrt(
        dx * dx +
        dy * dy +
        dz * dz
    )


def calculate_move_time(distance):
    if distance <= 0:
        return 0.0

    return distance / MOVE_SPEED


# ============================================================
# DIRECTION
# ============================================================

def get_direction(current, target):

    dx = target["x"] - current["x"]
    dy = target["y"] - current["y"]
    dz = target["z"] - current["z"]

    return {
        "x": 0 if dx == 0 else (1 if dx > 0 else -1),
        "y": 0 if dy == 0 else (1 if dy > 0 else -1),
        "z": 0 if dz == 0 else (1 if dz > 0 else -1)
    }


# ============================================================
# SWIPE
# ============================================================

def create_swipe(direction, duration):

    # แปลงทิศทางโลกเป็นทิศทางการเลื่อนหน้าจอ
    #
    # X = ซ้าย/ขวา
    # Y = ขึ้น/ลง
    # Z = ระยะลึก
    #
    # ตรงนี้เป็นค่ากลาง สามารถปรับตามเกมจริงได้

    center_x = 540
    center_y = 1200

    distance = 350

    end_x = center_x
    end_y = center_y

    if direction["x"] > 0:
        end_x += distance

    elif direction["x"] < 0:
        end_x -= distance

    if direction["y"] > 0:
        end_y -= distance

    elif direction["y"] < 0:
        end_y += distance

    return {
        "type": "swipe",
        "from": [center_x, center_y],
        "to": [end_x, end_y],
        "duration": round(duration, 3)
    }


# ============================================================
# NAVIGATION
# ============================================================

def navigate(current, target):

    distance = distance_3d(current, target)

    if distance <= GRID_SIZE:
        return {
            "type": "tap",
            "x": 540,
            "y": 1200,
            "duration": 0.05
        }

    direction = get_direction(current, target)

    move_time = calculate_move_time(distance)

    # ป้องกัน duration ยาวเกินไป
    move_time = min(move_time, 3.0)

    action = create_swipe(
        direction,
        move_time
    )

    return action


# ============================================================
# MAIN GAME CONTROL
# ============================================================

def control_game(data):

    current = data.get("position")
    target = data.get("target")

    if not isinstance(current, dict):
        raise ValueError("position ต้องเป็น XYZ")

    if not isinstance(target, dict):
        raise ValueError("target ต้องเป็น XYZ")

    for key in ("x", "y", "z"):

        if key not in current:
            raise ValueError(f"position ขาด {key}")

        if key not in target:
            raise ValueError(f"target ขาด {key}")

    current = {
        "x": float(current["x"]),
        "y": float(current["y"]),
        "z": float(current["z"])
    }

    target = {
        "x": float(target["x"]),
        "y": float(target["y"]),
        "z": float(target["z"])
    }

    current_grid = world_to_grid(
        current["x"],
        current["y"],
        current["z"]
    )

    target_grid = world_to_grid(
        target["x"],
        target["y"],
        target["z"]
    )

    distance = distance_3d(
        current,
        target
    )

    action = navigate(
        current,
        target
    )

    return {
        "current": current,
        "target": target,

        "grid": {
            "current": current_grid,
            "target": target_grid
        },

        "distance": round(distance, 3),

        "estimated_time": round(
            calculate_move_time(distance),
            3
        ),

        "action": action
    }


# ============================================================
# WEB
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# GAME API
# ============================================================

@app.route("/api/control", methods=["POST"])
def api_control():

    data = request.get_json(
        silent=True
    )

    if not isinstance(data, dict):

        return jsonify({
            "success": False,
            "error": "ต้องส่ง JSON"
        }), 400

    try:

        result = control_game(data)

        return jsonify({
            "success": True,
            "result": result
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ============================================================
# TAP API
# ============================================================

@app.route("/api/tap", methods=["POST"])
def api_tap():

    data = request.get_json(
        silent=True
    ) or {}

    try:

        x = float(data.get("x", 540))
        y = float(data.get("y", 1200))

        return jsonify({
            "success": True,
            "action": {
                "type": "tap",
                "x": x,
                "y": y
            }
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ============================================================
# SWIPE API
# ============================================================

@app.route("/api/swipe", methods=["POST"])
def api_swipe():

    data = request.get_json(
        silent=True
    ) or {}

    try:

        x1 = float(data.get("x1", 540))
        y1 = float(data.get("y1", 1200))

        x2 = float(data.get("x2", 540))
        y2 = float(data.get("y2", 800))

        duration = float(
            data.get("duration", 0.5)
        )

        return jsonify({
            "success": True,
            "action": {
                "type": "swipe",
                "from": [x1, y1],
                "to": [x2, y2],
                "duration": duration
            }
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 400


# ============================================================
# HEALTH
# ============================================================

@app.route("/api/health")
def health():

    return jsonify({
        "status": "online",
        "agent": "Game Control Engine",
        "grid_size": GRID_SIZE,
        "move_speed": MOVE_SPEED,
        "controls": [
            "tap",
            "swipe"
        ]
    })


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            10000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
