import os
import sys
from argparse import ArgumentParser
import base64
import hashlib
import hmac

from flask import Flask, request, abort
from linebot.v3.webhook import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage,
)

from openai import OpenAI


channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

parser = WebhookParser(channel_secret)
configuration = Configuration(access_token=channel_access_token)
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


def get_translation(message_text):
    """
    Translate a message from English to Japanese or vice versa using GPT-3.

    Parameters
    ----------
    message_text : str
        The message to be translated.

    Returns
    -------
    str
        The translated message.
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You will be provided either a sentence in English or in Japanese. Please translate the sentence into the other language.",
                },
                {
                    "role": "user", 
                    "content": f"{message_text}"
                },
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content
    except Exception as e:
        # pass the OpenAI response to the console, and a standard error message to the user
        print("An error occurred: ", e, f"\nResponse from OpenAI:\n{response}")
        return "An error occurred while translating this message. | このメッセージの翻訳中にエラーが発生しました。"


app = Flask(__name__)


@app.route("/callback", methods=["POST"])
def callback():
    """
    Callback function for LINE webhook.

    Returns
    -------
    str
        "OK" if successful.

    Raises
    ------
    400
        If the signature is invalid.

    Notes
    -----
    This function is called when a message is sent to the LINE bot.

    The message is translated using GPT-3 and then sent back to the user.

    The LINE API is used to send the translation back to the user.
    """

    # get LINE account details
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # verify the signature
    hash = hmac.new(channel_secret.encode('utf-8'), body.encode('utf-8'), hashlib.sha256).digest()
    computed_signature = base64.b64encode(hash).decode()

    if signature != computed_signature:
        app.logger.warning("Invalid signature received. ")
        abort(400)

    # try to read the event from LINE webhook, abort if failed
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then translate TextMessage in a reply to the user
    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            with ApiClient(configuration) as api_client:
                # retrieve translation from GPT-3 API
                translation = get_translation(event.message.text)

                # reply to user or in group chat with translation
                line_bot_api = MessagingApi(api_client)
                line_bot_api.reply_message_with_http_info(
                    ReplyMessageRequest(
                        reply_token=event.reply_token,
                        messages=[TextMessage(text=translation)],
                    )
                )

    return "OK"


if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage="Usage: python " + __file__ + " [--port <port>] [--help]"
    )
    arg_parser.add_argument("-p", "--port", type=int, default=8000, help="port")
    arg_parser.add_argument("-d", "--debug", default=False, help="debug")
    options = arg_parser.parse_args()

    app.run(debug=options.debug, port=options.port)
