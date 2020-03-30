import sys
import logging
import picamera
import picamera.array

from . import redis_client


WIDTH, HEIGHT = 640, 480
FRAMERATE = 24
HFLIP = True
ZOOM = (0.0, 0.0, 1.0, 1.0)
EV = 0


logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=" %I:%M:%S ",
    level="INFO",
)
logger = logging.getLogger(__name__)


class StreamOutput(picamera.array.PiRGBAnalysis):
    def __init__(self, camera, model):
        """Custom streaming output for the PiCamera"""
        super().__init__(camera)
        self.model = model
        self.array = None
        self.pose = None
        self.inference_time = None

    def analyze(self, array):
        """While recording is in progress, analyzes incoming array data"""
        self.array = array
        self.pose, self.inference_time = self.model.DetectPosesInImage(self.array)
        if self.pose:
            self.pose = max(self.pose, key=lambda pose: pose.score)
            redis_client.lpush("pose_score", self.pose.score.item(), max_size=5)
        redis_client.lpush("inference_time", self.inference_time, max_size=5)


class VideoStream(object):
    def __init__(
        self,
        resolution=(WIDTH, HEIGHT),
        framerate=FRAMERATE,
        hflip=HFLIP,
        zoom=ZOOM,
        ev=EV,
    ):
        """Creates a VideoStream from picamera for streaming and analyzing incoming data.
        Args:
          resolution: tuple, the resolution at which video recordings will be captured, in (width, height).
          framerate: int, the framerate video recordings will run (fps).
          hflip: flip view horizontally.
          zoom: the zoom applied to the camera’s input.
          ev: the exposure compensation level of the camera.
        """
        # Initiates a PiCamera instance
        self.camera = picamera.PiCamera()
        self.camera.resolution = resolution
        self.camera.framerate = framerate
        self.camera.hflip = hflip
        self.camera.zoom = zoom
        self.camera.exposure_compensation = ev
        logger.info(
            "PiCamera: resolution={} framerate={}".format(
                self.camera.resolution, self.camera.framerate
            )
        )

    def start(self, model):
        self.stream = StreamOutput(self.camera, model)
        self.camera.start_recording(self.stream, format="rgb")
        self.camera.wait_recording(2)
        logger.info("Recording started.")

    def __del__(self):
        logger.info("Closing PiCamera.")
        self.stream.close()
        self.camera.stop_recording()
        self.camera.close()

    def update(self):
        while not self.camera.closed:
            yield {
                "array": self.stream.array,
                "pose": self.stream.pose,
                "inference_time": self.stream.inference_time,
            }
