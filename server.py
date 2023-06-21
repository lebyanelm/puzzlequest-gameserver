"""
_________________________________
SERVER_NAME
Server description goes here
__________________________________
"""
import flask
import flask_cors
import os
import requests
import dotenv
import traceback
from models.response import Response
from flask_socketio import SocketIO, emit


"""
__________________________________
DEVELOPMENTAL ENVIRONMENT VARIABLES
__________________________________
"""
if os.environ.get("environment") != "production":
    dotenv.load_dotenv()


"""
__________________________________
SERVER INSTANCE SETUP
__________________________________
"""
server_instance = flask.Flask(
    __name__, static_folder="./assets/", static_url_path="/server_name/assets/"
)
flask_cors.CORS(server_instance, resources={r"*": {"origins": "*"}})


# Socket.IO added functionality
socketio_server = SocketIO(server_instance, cors_allowed_origins="*")


# STATE MANAGEMENT
CURRENT_SENTENCE = dict()
NEXT_SENTENCES = list()


@socketio_server.on("connect")
def connect():
    print("A client has connected.")
    emit("connected", {"data": "Connected"})


# WHEN A KEY HAS BEEN ENTERED.
@socketio_server.on("keydown")
def keydown_event(data):
    global CURRENT_SENTENCE
    CURRENT_SENTENCE = data

    emit("keydown", data, broadcast=True)


# WHEN A KEY HAS BEEN ENTERED.
@socketio_server.on("input_completed")
def input_completed(data):
    emit("input_completed", data, broadcast=True)


@socketio_server.on("disconnect")
def test_disconnect():
    print("Client disconnected.")


def request_response(request):
    print("Generating words.")
    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-3.5-turbo",
            "temperature": 1,
            "messages": [{"role": "user", "content": request}],
        },
    )

    if r.status_code == 200:
        response = r.json()["choices"][0]["message"]["content"]
        print(response)
        return response
    else:
        Exception("Error genering words.")


def generate_random_sentence():
    return request_response(
        request="Generate totally random sentence: Rules are, 1. no punctions/period/apostrophe/special characters allowed, 2. must be less than 4, 4. must be goofy, 5. can be tricky and creative, 6. no plural words, 7. each word must not be longer than 12 characters, 8. can be an academic sentence including sience, and 10. must be creative."
    )


def get_a_word_clue(word):
    return request_response(
        request=f"Give a clue for the following word: {word}. Rules, don't mention the exact word, be more creative with the clue and make it fun to guess."
    )


def get_a_word_example(word):
    return request_response(
        request=f'Give me an example in which the word "{word}" can be used. Replace the "{word}" with underscores (_) in the response for a guess game.'
    )


def get_part_of_speech(word):
    return request_response(
        request=f"In a one word answer, whats the part of speech for the following word: {word}?"
    )


"""
__________________________________
SERVER INSTANCE ROUTES
__________________________________
"""


# Returns status of the server
@server_instance.route("/words/sentence", methods=["GET"])
@flask_cors.cross_origin()
def status():
    global CURRENT_SENTENCE

    try:
        if (
            CURRENT_SENTENCE.get("is_completed") is None
            or CURRENT_SENTENCE.get("is_completed") is True
        ):
            # Generate the random sentence that will be used for the clues
            random_sentence_words = generate_random_sentence()[:-1].lower().split()

            # Find all the clues related to the words in the sentences
            clues = {}
            for random_sentence_word in random_sentence_words:
                clues[random_sentence_word] = dict(
                    partOfSpeech=get_part_of_speech(random_sentence_word),
                    meaning=get_a_word_clue(random_sentence_word),
                    example=get_a_word_example(random_sentence_word),
                    synonyms=[],
                )

                if clues[random_sentence_word]["example"]:
                    clues[random_sentence_word]["example"].replace(
                        random_sentence_word, "_"
                    )

            # Algorithm for the return format.
            text = {
                # MAX: 12 CHARS.
                "lines": [[]],
                "all": " ".join(random_sentence_words),
            }
            number_of_lines = round(len(text["all"]) / 12) + 1
            text["lines"] = text["lines"] * number_of_lines

            added_words = []

            for line_index, _ in enumerate(text["lines"]):
                for word_index, random_sentence_word in enumerate(
                    random_sentence_words
                ):
                    if (
                        len(text["lines"][line_index]) < 12
                        and len(text["lines"][line_index]) + len(random_sentence_word)
                        <= 12
                    ):
                        if random_sentence_word not in added_words:
                            text["lines"][line_index] = [
                                *text["lines"][line_index],
                                *list(random_sentence_word),
                            ]
                            if len(text["lines"][line_index]) != 12:
                                text["lines"][line_index].append(" ")

                                # Check if the next word will fit. Else add empty spaces.
                                if (word_index != len(random_sentence_words) - 1) and (
                                    len(random_sentence_words[word_index - 1])
                                    + len(text["lines"][line_index])
                                    > 12
                                ):
                                    number_of_space = 12 - len(
                                        text["lines"][line_index]
                                    )
                                    spaces = (" ." * number_of_space).split(".")[0:-1]

                                    text["lines"][line_index] = [
                                        *text["lines"][line_index],
                                        *spaces,
                                    ]
                            added_words.append(random_sentence_word)
                    else:
                        break

            # Build a letter index.
            columns = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]
            letter_indices = {}

            for line_row, row in enumerate(text["lines"]):
                for line_column, letter in enumerate(row):
                    if letter_indices.get(letter) is None:
                        letter_indices[letter] = f"{columns[line_column]}{line_row + 1}"

            sentence = dict(
                is_completed=False,
                text=text,
                clues=clues,
                letter_indices=letter_indices,
                corrected=dict(),
            )

            CURRENT_SENTENCE = sentence

        print(CURRENT_SENTENCE["corrected"], "corrected words.")
        return Response(cd=200, d=CURRENT_SENTENCE).to_json()
    except:
        print(traceback.format_exc())
        return Response(cd=500).to_json()


if __name__ == "__main__":
    socketio_server.run(server_instance, port=80)
