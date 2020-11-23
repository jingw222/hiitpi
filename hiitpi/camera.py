import sys
import logging
import picamera
import picamera.array


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
    """Custom streaming output for the PiCamera"""

    def setup(self, model, redis):
        """
        Args:
          model: PoseEngine for TensorFlow Lite models.
          redis: RedisClient.
        """
        self.array = None
        self.pose = None
        self.inference_time = None
        self.model = model
        self.redis = redis
        self.redis.set("reps", 0)
        self.redis.set("pace", 0)

    def analyze(self, array):
        """While recording is in progress, analyzes incoming array data"""
        self.array = array
        self.pose, self.inference_time = self.model.DetectPosesInImage(self.array)
        if self.pose:
            self.pose = max(self.pose, key=lambda pose: pose.score)
            self.redis.lpush("pose_score", self.pose.score.item(), max_size=5)
        self.redis.lpush("inference_time", self.inference_time, max_size=5)


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
        # PiCamera configurations
        self.resolution = resolution
        self.framerate = framerate
        self.hflip = hflip
        self.zoom = zoom
        self.ev = ev
        logger.info(
            f"PiCamera configurations: "
            f"resolution={self.resolution}, framerate={self.framerate}, "
            f"hflip={self.hflip}, zoom={self.zoom}, ev={self.ev}"
        )
        self.closed = None

    def setup(self, model, redis):
        """Initiates a PiCamera, attaches a StreamOutput and starts recording.
        Args:
          model: PoseEngine for TensorFlow Lite models.
          redis: RedisClient.
        """

        # Builds and sets up a PiCamera
        self.camera = picamera.PiCamera()
        self.camera.resolution = self.resolution
        self.camera.framerate = self.framerate
        self.camera.hflip = self.hflip
        self.camera.zoom = self.zoom
        self.camera.exposure_compensation = self.ev

        # Creates and sets up a StreamOutput
        self.stream = StreamOutput(self.camera)
        self.stream.setup(model=model, redis=redis)

        self.closed = False

    def start(self):
        """Starts recording to the stream."""
        self.camera.start_recording(self.stream, format="rgb")
        self.camera.wait_recording(2)
        logger.info("Recording started.")

    def close(self):
        """Closes the camera and the stream."""
        self.camera.stop_recording()
        self.camera.close()
        self.stream.close()
        logger.info("Recording stopped.")

        self.closed = True

    def update(self):
        """Streams outputs from the camera."""
        while not self.closed:
            yield {
                "array": self.stream.array,
                "pose": self.stream.pose,
                "inference_time": self.stream.inference_time,
            }
