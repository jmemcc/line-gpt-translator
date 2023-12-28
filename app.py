import os
import sys
from argparse import ArgumentParser

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
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print("An error occurred: ", e, f"\nResponse from OpenAI:\n{response}")
        return "An error occurred while translating this message. | このメッセージの翻訳中にエラーが発生しました。"

app = Flask(__name__)

@app.route("/callback", methods=["POST"])
def callback():
    # get LINE account details
    signature = request.headers["X-Line-Signature"]
    
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # try to read the event from LINE webhook, abort if failed
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then translate and reply
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessageContent):
            continue
        with ApiClient(configuration) as api_client:
            # retrieve translation from GPT-4 API
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
