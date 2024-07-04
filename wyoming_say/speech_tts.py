import os
import logging
import tempfile
import time
import mac_say


log = logging.getLogger(__name__)


FORMAT_STRING = "LEI16@22050"  # Don't ask me how I figured this one out


class SpeechTTS:
    """Class to handle Speech TTS."""

    def __init__(self, args) -> None:
        """Initialize."""
        log.debug("Initialize Speech TTS")
        self.args = args
        self.tmpdir = tempfile.TemporaryDirectory()

    def synthesize(self, text, voice=None):
        """Synthesize text to speech."""
        log.debug(f"Requested TTS for [{text}]")
        if voice is None:
            voice = self.args.voice
        file_name = os.path.join(
            self.tmpdir.name,
            f"{time.monotonic_ns()}.wav")
        mac_say.say([
            "-v", voice,
            "-o", file_name,
            "--data-format", FORMAT_STRING,
            text])
        return file_name
    
    def __del__(self):
        self.tmpdir.cleanup()
