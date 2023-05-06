import os
import json
import openai
import tempfile
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent,
    AudioMessage,
    TextSendMessage,
    FileMessage,
    VideoMessage,
)

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_CHANNEL_ACCESS_TOKEN"]
LINE_CHANNEL_SECRET = os.environ["LINE_CHANNEL_SECRET"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)
openai.api_key = OPENAI_API_KEY

okResponse = {
    "statusCode": 200,
    "headers": {"Content-Type": "text/plain"},
    "body": "Hello, CDK!",
}
errorResponse = {
    "statusCode": 400,
    "headers": {"Content-Type": "text/plain"},
    "body": "Bad Request",
}

mimeTypeToExtension = {"audio/x-m4a": "m4a", "audio/mpeg3": "mp3", "video/mp4": "mp4"}


def lambda_handler(event, context):
    print("request: {}".format(json.dumps(event)))
    signature = event["headers"]["x-line-signature"]
    body = event["body"]

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return errorResponse

    return okResponse


@handler.add(MessageEvent, message=[AudioMessage, FileMessage, VideoMessage])
def handle_audio_message(line_event):
    message_content = line_bot_api.get_message_content(line_event.message.id)
    extension = mimeTypeToExtension[message_content.content_type]
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_file = os.path.join(tmp_dir, f"{line_event.message.id}.{extension}")
        with open(tmp_file, "wb") as fd:
            for chunk in message_content.iter_content():
                fd.write(chunk)
        audio_file = open(tmp_file, "rb")
        transcript = openai.Audio.transcribe("whisper-1", audio_file)
    line_bot_api.reply_message(
        line_event.reply_token, TextSendMessage(text=transcript.text)
    )
