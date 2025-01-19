import asyncio
import itertools
import os
import traceback
from pprint import pprint
from typing import Generator

import pyaudio
from dotenv import load_dotenv
from google import genai
from google.cloud import texttospeech

from tools.picnic_tools import handle_picnic_tool_operations
from tools.tool_descriptions import tools

load_dotenv()

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024
MODEL = "models/gemini-2.0-flash-exp"
pya = pyaudio.PyAudio()
RESPONSE_MODEL = "TEXT"  # or "AUDIO" <- AUDIO is not well-supported yet...

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"), http_options={"api_version": "v1alpha"})
text_to_speach_client = texttospeech.TextToSpeechClient()

CONFIG = {"generation_config": {"response_modalities": [RESPONSE_MODEL], "temperature": 0},
          "system_instruction": "You are a shopping assistant called Picnic Pal 3000 for the online grocery store "
                                "Picnic.",
          "tools": [tools]}
streaming_config = texttospeech.StreamingSynthesizeConfig(
    voice=texttospeech.VoiceSelectionParams(name="en-US-Journey-D", language_code="en-US"))
config_request = texttospeech.StreamingSynthesizeRequest(streaming_config=streaming_config)


class AudioLoop:
    def __init__(self) -> None:
        self.audio_in_queue = None
        self.out_queue = None
        self.session = None
        self.send_text_task = None
        self.receive_audio_task = None
        self.play_audio_task = None
        self.audio_stream = None

    async def send_text(self) -> None:
        while True:
            text = await asyncio.to_thread(
                input,
                "message > \n",
            )
            if text.lower() == "q":
                break
            await self.session.send(text or ".", end_of_turn=True)

    async def send_realtime(self) -> None:
        while True:
            msg = await self.out_queue.get()
            await self.session.send(msg)

    async def listen_audio(self) -> None:
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def receive_audio(self) -> None:
        """Background task to reads from the websocket and write pcm chunks to the output queue"""
        while True:
            function_responses = []
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(text, end="")
                    if RESPONSE_MODEL == "TEXT":
                        data = await self.stream_text_to_speech(text)
                        self.audio_in_queue.put_nowait(data)
                    continue
                if _ := response.tool_call:
                    function_calls = response.tool_call.function_calls
                    for function_call in function_calls:
                        name = function_call.name
                        args = function_call.args
                        call_id = function_call.id
                        try:
                            response = handle_picnic_tool_operations(name, args, call_id)
                            function_responses.append(response)
                        except Exception as e:
                            print(f"Error executing {name} function with error: {e}")
                    pprint(function_responses, width=180, indent=2, compact=False)
                    # Send function result back to Gemini
                    await self.session.send(function_responses)
                    continue
            if RESPONSE_MODEL == "AUDIO":
                # If you interrupt the model, it sends a turn_complete.
                # For interruptions to work, we need to stop playback.
                # So empty out the audio queue because it may have loaded
                # much more audio than has played yet.
                while not self.audio_in_queue.empty():
                    self.audio_in_queue.get_nowait()

    async def play_audio(self) -> None:
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)

    async def run(self) -> None:
        try:
            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,  # noqa
                asyncio.TaskGroup() as tg,
            ):
                self.session = session
                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)
                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            pass
        except ExceptionGroup as EG:
            self.audio_stream.close()
            traceback.print_exception(EG)

    async def stream_text_to_speech(self, text: str) -> bytes:
        def request_generator() -> Generator:
            yield texttospeech.StreamingSynthesizeRequest(
                input=texttospeech.StreamingSynthesisInput(text=f" {text}"))  # noqa

        streaming_responses = text_to_speach_client.streaming_synthesize(
            itertools.chain([config_request], request_generator()))
        audio_content = bytearray()
        for response in streaming_responses:
            audio_content.extend(response.audio_content)
        return bytes(audio_content)


if __name__ == "__main__":
    main = AudioLoop()
    asyncio.run(main.run())
