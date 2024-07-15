from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room, send
import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)

deck = []
suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
values = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]
rooms = {}
usids = {}

def createDeck():
    global deck
    deck = [{"suit": suit, "value": value} for suit in suits for value in values]

def shuffleDeck():
    global deck
    random.shuffle(deck)

def dealCards(room):
    createDeck()
    shuffleDeck()
    global rooms
    for player_name in rooms[room].keys():
        rooms[room][player_name] = [deck.pop() for _ in range(12)]

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break
    return code


@app.route("/", methods=["GET", "POST"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template(
                "home.html", error="Please enter a name", code=code, name=name
            )

        if join != False and not code:
            return render_template(
                "home.html", error="Please enter a room code", code=code, name=name
            )

        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = dict()
            usids[room] = dict()
            print(f"Room {rooms} created")

        elif code not in rooms:
            return render_template(
                "home.html", error="Room not found", code=code, name=name
            )

        session["room"] = room
        session["name"] = name

        return redirect(url_for("room",player_id=name))

    return render_template("home.html")


@app.route("/room/<player_id>")
def room(player_id):
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template("room.html", code=room)


@socketio.on("message")
def message(data):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        return
    content = {"name": name, "message": data["data"]}
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{name} sent message to room {room}: {data['data']}")


@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    usids[room][name] = request.sid
    if not room or not name:
        print("no room or name")
        return
    if room not in rooms:
        print("room not in rooms")
        leave_room(room)
        return
    if len(rooms[room].keys()) >= 5:
        print("room full")
        leave_room(room)
        return
    join_room(room)
    print(f"num {len(rooms[room].keys())}")
    send({"name": name, "message": "joined the room"}, to=room)
    rooms[room][name] = []
    print(f"{name} joined room {room}")

    if len(rooms[room].keys()) == 4:
        print("dealing cards")
        createDeck()
        shuffleDeck()
        dealCards(room)
        for player_name in rooms[room].keys():
            send({"name": player_name, "message": str(rooms[room][player_name])}, to=usids[room][player_name])
            print(usids[room][player_name],"\n")
            print(f"{player_name} has been dealt {rooms[room][player_name]}")


@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        del rooms[room][name]
        if len(rooms[room].keys()) <= 0:
            del rooms[room]

    send({"name": name, "message": "left the room"}, to=room)

if __name__ == "__main__":
    socketio.run(app, debug=True)
