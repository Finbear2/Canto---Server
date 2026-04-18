from quart import Quart, jsonify, request, render_template
from shazamio import Shazam
import aiohttp
import sqlite3
import random

app = Quart(__name__)
shazam = Shazam()

secret = "Fish"
muted = False
name = "ERROR"

DB = "database/songs.db"

with open("logo.txt", "r") as f:
    print(f.read())

# WEB UI
@app.route("/")
async def recent():
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "http://127.0.0.1:5000/sql/get",
            headers={
                "key": secret,
                "limit": str(200)
            }) as resp:
            if resp.status not in (200, 204):
                print(f"\nDatabase to get data from database! Error code {resp.status}")
                return "ERROR"
            else:
                data = await resp.json()

    for song in data:                                                   
        red = random.randint(220,255)
        green = random.randint(220,255)
        blue = random.randint(220,255)
        song["colour"] = dict()
        song["colour"]["pastel"] = f"rgb({red}, {green}, {blue})"
        song["colour"]["button"] = f"rgb({red-50}, {green-50}, {blue-50})"

    return await render_template("index.html", data=data)

#     A      PPPPPPP  IIIIIII
#    A A     P     P     I
#   AAAAA    PPPPPP      I
#  A     A   P           I 
# A       A  P        IIIIIII 

# SQL
@app.route("/sql/init", methods=["POST"])
async def initSql():

    key = request.headers.get("key")
    if key != secret:
        return jsonify({"error": "invalid key"}), 401

    con = sqlite3.connect(DB)
    cursor = con.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            artist TEXT,
            album TEXT,
            shazamLink TEXT,
            spotifyLink TEXT,
            starred INTEGER DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    con.commit()
    print("Initialised database!")

    con.close()

    return jsonify({"done": "databse initialised"}), 200

@app.route("/sql/get", methods=["POST"])
async def getSql():

    key = request.headers.get("key")
    if key != secret:
        return jsonify({"error": "invalid key"}), 401

    limit = request.headers.get("limit")
    limit = int(limit)

    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    
    cursor.execute("SELECT * FROM songs ORDER BY timestamp DESC LIMIT ?", (limit,))
    rows = [dict(row) for row in cursor.fetchall()]
    con.close()
    return jsonify(rows)

@app.route("/sql/write", methods=["POST"])
async def write():

    key = request.headers.get("key")
    if key != secret:
        return jsonify({"error": "invalid key"}), 401

    con = sqlite3.connect(DB)
    cursor = con.cursor()

    data = await request.get_json()

    print("\nWriting to database...")
    cursor.execute("INSERT INTO songs (title, artist, album, shazamLink, spotifyLink) VALUES (?, ?, ?, ?, ?)",
            (data["title"], data["artist"], data["album"], data["link"]["shazam"], data["link"]["spotify"]))
    con.commit()
    print("Saved to database!")

    con.close()
    return jsonify({"done": "database has been writen to"}), 200


# SHAZAM
@app.route("/identify", methods=["POST"])
async def apiCall():

    key = request.headers.get("key")
    if key != secret:
        return jsonify({"error": "invalid key"}), 401

    audio = await request.get_data()

    if not audio:
        return jsonify({"error": "no file uploaded"}), 400

    result = await shazam.recognize_song(audio)

    return jsonify(result)

# STATUS
@app.route("/status", methods=["POST"])
async def statusCall():
    global name

    key = request.headers.get("key")
    if key != secret:
        return jsonify({"error": "invalid key"}), 401

    key = request.headers.get("boot")
    if key == "true":
        name = request.headers.get("name")

    data = {}

    data["muted"] = muted
    data["name"] = name

    return jsonify(data)

# # STATUS
# @app.route("/status", methods=["POST"])
# async def statusCall():
#     global name

#     key = request.headers.get("key")
#     if key != secret:
#         return jsonify({"error": "invalid key"}), 401

#     key = request.headers.get("boot")
#     if key == "true":
#         name = request.headers.get("name")

#     data = {}

#     data["muted"] = muted
#     data["name"] = name

#     return jsonify(data)


if __name__ == "__main__":

    import asyncio
    asyncio.run(app.run(host="0.0.0.0", port=5000))