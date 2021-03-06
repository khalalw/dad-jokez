import requests
from db import db, add_joke_to_db, does_joke_exist
from twilio.rest import Client
import datetime


def get_dad_joke():
    resp = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "text/plain"})
    return resp.content.decode("utf-8")


def handle_response(incoming_msg: str):
    handler = {
        "dad": "Thank you for signing up for your daily dose of dad jokes. You'll receive one joke "
        "every day around 12PM EST. To opt out at any time, reply 9 or STOP.",
        # Twilio's API handles STOP and HELP responses, so these will do
        "9": "You are now unsubscribed from receiving daily dad jokes.",
        "7": "Dad Jokes:\n\nIf you'd like to receive an automated dad joke"
        " once a day, reply DAD. To stop receiving messages completely, "
        "reply STOP",
    }

    return handler.get(incoming_msg, handler["7"])


def send_daily_message(message_client: Client, outgoing_number: str):
    joke = get_dad_joke()

    # prevent duplicate jokes
    while does_joke_exist(joke):
        joke = get_dad_joke()
    
    add_joke_to_db(joke)
    
    today = datetime.date.today()
    month = today.month
    day = today.day
    message = f"Daily Dad Joke - {month}/{day}:\n\n{joke}"

    for sub in db.sub_list.find():
        subscriber_number = sub["number"]
        message_client.messages.create(
            body=message, from_=outgoing_number, to=subscriber_number
        )


def is_number_valid(phone_number: str):
    if len(phone_number) != 12:
        return False
    if phone_number[:2] != "+1":
        return False

    return True
