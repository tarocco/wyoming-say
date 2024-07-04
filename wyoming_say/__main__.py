import os
from argparse import ArgumentParser
import asyncio
import contextlib
import logging
from functools import partial
from collections import defaultdict

from wyoming.info import Attribution, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncServer

from handler import SpeechEventHandler
from version import __version__

import mac_say


log = logging.getLogger(__name__)


def _voice_info2(string:str):
    # Bugfix for string splitting
    nl, desc = [s for s in string.split("#", 1) if s]
    lang, name = [s[::-1].strip() for s in nl.strip()[::-1].split(None, 1)]
    return name, lang, desc.lstrip()


# Monkey patch 🐒🐵
mac_say._voice_info = _voice_info2


# Unused
# def get_variants(voices):
#     variants = defaultdict(dict)
#     for name, lang, desc in voices:
#         key = name.split("(", 1)[0].rstrip()
#         variants[key][lang] = desc
#     return variants


def get_default_description(variants):
    """ Please don't shoot me """
    # Try US English
    if "en_US" in variants:
        return variants["en_US"]
    # Try GB English
    if "en_GB" in variants:
        return variants["en_GB"]
    # Try any other language (just pick one)
    return next(v for v in variants.values())


async def main() -> None:
    logging.basicConfig(level=os.getenv("LOGLEVEL", "INFO"))
    parser = ArgumentParser()
    parser.add_argument(
        "--uri", default="tcp://0.0.0.0:10200", help="unix:// or tcp://"
    )
    parser.add_argument("--samples-per-chunk", type=int, default=1024)

    #parser.add_argument("--language", type=str, default="en_US")
    #parser.add_argument("--voice-name", type=str, default=None)
    args = parser.parse_args()
    #mac_voices = mac_say.voices(args.language)
    mac_voices = mac_say.voices()

    # We need to preserve individual "names" of voices per language.
    # Apple added (Language (Nation)) suffixes to each voice name.
    # Otherwise they won't be distinguishable by the Wyoming API.

    #variants = get_variants(mac_voices)  # Unused
    voices = [
        TtsVoice(name=name,
                 #description=get_default_description(variants),  # Unused
                 #description=desc,
                 description=name,  # Home Assistant compatibility
                 attribution=Attribution(
                     name="Apple",
                     url="https://www.apple.com/accessibility/speech/"
                 ),
                 installed=True,
                 version=__version__,
                 #languages=list(variants.keys()))  # Unused
                 languages=[lang])
        #for name, variants in variants.items()  # Unused
        for name, lang, desc in mac_voices
    ]
    
    wyoming_info = Info(
        tts=[
            TtsProgram(
                name="plaintalk",
                description="Apple's text-to-speech for Mac",
                attribution=Attribution(
                     name="Apple",
                     url="https://www.apple.com/accessibility/speech/"
                ),
                installed=True,
                version=__version__,
                #voices=sorted(voices, key=lambda v: v.name),
                voices=voices
            )
        ]
    )

    server = AsyncServer.from_uri(args.uri)

    log.info("Ready")

    await server.run(
        partial(
            SpeechEventHandler,
            wyoming_info,
            args
        )
    )


if __name__ == "__main__":
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())