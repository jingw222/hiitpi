import sys
import time
import logging
import collections
import numpy as np
from PIL import Image, ImageDraw


logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=" %I:%M:%S ",
    level="INFO",
)

logger = logging.getLogger(__name__)

EDGES = (
    ("nose", "left eye"),
    ("nose", "right eye"),
    ("nose", "left ear"),
    ("nose", "right ear"),
    ("left ear", "left eye"),
    ("right ear", "right eye"),
    ("left eye", "right eye"),
    ("left shoulder", "right shoulder"),
    ("left shoulder", "left elbow"),
    ("left shoulder", "left hip"),
    ("right shoulder", "right elbow"),
    ("right shoulder", "right hip"),
    ("left elbow", "left wrist"),
    ("right elbow", "right wrist"),
    ("left hip", "right hip"),
    ("left hip", "left knee"),
    ("right hip", "right knee"),
    ("left knee", "left ankle"),
    ("right knee", "right ankle"),
)


class Annotator(object):
    """Annotates video streaming output with a drawing overlay."""

    def __init__(self):
        self._init_time = time.perf_counter()
        self._rendering_time = collections.deque([self._init_time], maxlen=30)

    def annotate(self, output):
        self._rendering_time.append(time.perf_counter())
        rendering_fps = len(self._rendering_time) / (
            self._rendering_time[-1] - self._rendering_time[0]
        )

        img = Image.fromarray(output["array"])
        draw = ImageDraw.Draw(img, "RGBA")

        self.draw_pose(draw, output["pose"])

        text_lines = [
            "Inference time: {:.1f}ms ({:.1f}fps)".format(
                output["inference_time"], 1000 / output["inference_time"]
            ),
            "Rendering time: {:.1f}ms ({:.1f}fps)".format(
                1000 / rendering_fps, rendering_fps
            ),
            "",
        ]

        workout = output["workout"]
        if workout.stats is not None:
            text_lines.extend(
                ["{}: {:.1f}".format(k, v) for k, v in workout.stats.items()]
            )

        self.draw_text(draw, 10, 10, text="\n".join(text_lines))

        return np.asarray(img)

    def draw_text(self, draw, x, y, text):
        draw.text(xy=(x + 1, y + 1), text=text, fill="black")
        draw.text(xy=(x, y), text=text, fill="lightgray")

    def draw_circle(self, draw, x, y, r, width, alpha):
        draw.ellipse(
            [(x - r, y - r), (x + r, y + r)],
            fill=(0, 255, 255, int(255 * alpha)),
            outline="yellow",
            width=width,
        )

    def draw_line(self, draw, xy):
        draw.line(xy, fill="yellow", width=2)

    def draw_pose(self, draw, pose, threshold=0.2):
        if pose:
            xys = {}
            for label, keypoint in pose.keypoints.items():
                if keypoint.score < threshold:
                    continue

                y = int(keypoint.yx[0])
                x = int(keypoint.yx[1])

                xys[label] = (x, y)
                self.draw_circle(draw, x, y, r=3, width=1, alpha=keypoint.score)

            for a, b in EDGES:
                if a not in xys or b not in xys:
                    continue
                ax, ay = xys[a]
                bx, by = xys[b]
                self.draw_line(draw, [(ax, ay), (bx, by)])
