import sys
import logging
import cv2

from .annotation import Annotator


logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=" %I:%M:%S ",
    level="INFO",
)

logger = logging.getLogger(__name__)


def gen(camera, workout):
    """Streams and analyzes video contents while overlaying stats info
    Args:
      camera: a VideoStream object.
      workout: either an object of a subclass from Workout or "None" 
    Returns:
      bytes, the output image data
    """

    annotator = Annotator()
    if workout != "None":
        workout = workout()

    # Gets video frames from the PiCamera
    for output in camera.update():

        if workout != "None":
            # Compute workout stats
            workout.update(output["pose"])
            output["workout"] = workout

            # Annotates the image and encodes the raw RGB data into JPEG format
            output["array"] = annotator.annotate(output)
            img = cv2.cvtColor(output["array"], cv2.COLOR_RGB2BGR)

        else:
            img = cv2.blur(output["array"], (32, 32))
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

        ret, buf = cv2.imencode(".jpeg", img)

        yield (
            b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + buf.tobytes() + b"\r\n\r\n"
        )
