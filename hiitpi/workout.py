import sys
import logging
import time
import itertools
import collections
import numpy as np

from . import redis_client


logging.basicConfig(
    stream=sys.stdout,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt=" %I:%M:%S ",
    level="DEBUG",
)

logger = logging.getLogger(__name__)


class Edge:
    __slots__ = ["k_a", "k_b", "vec", "norm", "center", "score"]

    def __init__(self, k_a, k_b):
        self.k_a = k_a
        self.k_b = k_b
        self.vec = self.k_a.yx - self.k_b.yx
        self.norm = np.linalg.norm(self.vec)
        self.center = (self.k_a.yx + self.k_b.yx) / 2
        self.score = min(self.k_a.score, self.k_b.score)

    def __repr__(self):
        return "Edge({} -> {}, {})".format(self.k_a.k, self.k_b.k, self.vec)

    def __invert__(self):
        return Edge(self.k_b, self.k_a)

    def find_angle(self, edge):
        cosang = np.dot(self.vec, edge.vec)
        sinang = np.linalg.norm(np.cross(self.vec, edge.vec))
        angle = np.arctan2(sinang, cosang)
        return np.degrees(angle)


class Joint:
    __slots__ = ["e_a", "e_b", "angle"]

    def __init__(self, e_a, e_b):
        self.e_a = e_a
        self.e_b = e_b
        self.angle = self.e_a.find_angle(self.e_b)

    def __repr__(self):
        return "Joint({}, {}, {})".format(self.e_a, self.e_b, self.angle)


class Workout:
    """Base class for tracking workout progress with movement analysis"""

    def __init__(self, n_keystates):
        self.THRESHOLD = 0.2
        self.N_KEYSTATES = n_keystates
        self.KEYSTATES = itertools.cycle(range(1, self.N_KEYSTATES + 1))
        self._prev_state = None
        self._next_state = next(self.KEYSTATES)
        self.stats = None
        self.reps = 0
        self.pace = 0
        self._init_time = time.perf_counter()
        self._reps_time = collections.deque([], maxlen=32)

        redis_client.set("reps", self.reps)
        redis_client.set("pace", self.pace)

    def get_stats(self, pose):
        raise NotImplemented

    def get_state(self, stats):
        raise NotImplemented

    def update(self, pose):
        if pose:
            self.stats = self.get_stats(pose)
            state = self.get_state(self.stats)

            if state != 0 and state != self._prev_state and state == self._next_state:
                self._prev_state = state
                self._next_state = next(self.KEYSTATES)
                if state == self.N_KEYSTATES:
                    self._reps_time.append(time.perf_counter())
                    if self.reps > 1:
                        self.pace = (len(self._reps_time) - 1) / (
                            self._reps_time[-1] - self._reps_time[0]
                        )
                    self.reps += 1
                    redis_client.set("reps", self.reps)
                    redis_client.set("pace", self.pace)


class ToeTap(Workout):
    name = "Toe Tap"

    def __init__(self, *args, **kwargs):
        super().__init__(n_keystates=2, *args, **kwargs)
        self.KEYPOINTS = [
            "left hip",
            "right hip",
            "left ankle",
            "right ankle",
            "left elbow",
            "left shoulder",
            "left wrist",
            "right elbow",
            "right shoulder",
            "right wrist",
        ]

    def get_stats(self, pose):
        kps = pose.keypoints

        if all(kps[k].score > self.THRESHOLD for k in self.KEYPOINTS):

            e_hips = Edge(kps["left hip"], kps["right hip"])
            e_ankles = Edge(kps["left ankle"], kps["right ankle"])
            e_lelbow_lshoulder = Edge(kps["left elbow"], kps["left shoulder"])
            e_lelbow_lwrist = Edge(kps["left elbow"], kps["left wrist"])
            e_relbow_rshoulder = Edge(kps["right elbow"], kps["right shoulder"])
            e_relbow_rwrist = Edge(kps["right elbow"], kps["right wrist"])

            j_lelbow = Joint(e_lelbow_lshoulder, e_lelbow_lwrist)
            j_relbow = Joint(e_relbow_rshoulder, e_relbow_rwrist)

            return {
                "e_hips_norm": e_hips.norm,
                "e_ankles_norm": e_ankles.norm,
                "j_lelbow_angle": j_lelbow.angle,
                "j_relbow_angle": j_relbow.angle,
            }
        else:
            return None

    def get_state(self, stats):
        if stats is not None:
            if stats["e_ankles_norm"] <= stats["e_hips_norm"]:
                if stats["j_lelbow_angle"] >= 90 and stats["j_relbow_angle"] <= 90:
                    return 1
                elif stats["j_relbow_angle"] >= 90 and stats["j_lelbow_angle"] <= 90:
                    return 2
                else:
                    return 0
            else:
                return 0
        else:
            return 0


class JumpingJacks(Workout):
    name = "Jumping Jacks"

    def __init__(self, *args, **kwargs):
        super().__init__(n_keystates=2, *args, **kwargs)
        self.KEYPOINTS = [
            "left hip",
            "right hip",
            "left ankle",
            "right ankle",
            "left elbow",
            "left shoulder",
            "right elbow",
            "right shoulder",
        ]

    def get_stats(self, pose):
        kps = pose.keypoints

        if all(kps[k].score > self.THRESHOLD for k in self.KEYPOINTS):

            e_hips = Edge(kps["left hip"], kps["right hip"])
            e_ankles = Edge(kps["left ankle"], kps["right ankle"])
            e_lshoulder_lelbow = Edge(kps["left shoulder"], kps["left elbow"])
            e_lshoulder_lhip = Edge(kps["left shoulder"], kps["left hip"])
            e_rshoulder_relbow = Edge(kps["right shoulder"], kps["right elbow"])
            e_rshoulder_rhip = Edge(kps["right shoulder"], kps["right hip"])

            j_lshoulder = Joint(e_lshoulder_lelbow, e_lshoulder_lhip)
            j_rshoulder = Joint(e_rshoulder_relbow, e_rshoulder_rhip)

            return {
                "e_hips_norm": e_hips.norm,
                "e_ankles_norm": e_ankles.norm,
                "j_lshoulder_angle": j_lshoulder.angle,
                "j_rshoulder_angle": j_rshoulder.angle,
            }
        else:
            return None

    def get_state(self, stats):
        if stats is not None:
            if (
                stats["e_ankles_norm"] <= stats["e_hips_norm"]
                and stats["j_lshoulder_angle"] <= 30
                and stats["j_rshoulder_angle"] <= 30
            ):
                return 1
            elif (
                stats["e_ankles_norm"] >= stats["e_hips_norm"] * 1.5
                and stats["j_lshoulder_angle"] >= 110
                and stats["j_rshoulder_angle"] >= 110
            ):
                return 2
            else:
                return 0
        else:
            return 0


class PushUp(Workout):
    name = "Push Up"

    def __init__(self, *args, **kwargs):
        super().__init__(n_keystates=2, *args, **kwargs)
        self.KEYPOINTS = [
            "left elbow",
            "left shoulder",
            "left wrist",
            "right elbow",
            "right shoulder",
            "right wrist",
        ]

    def get_stats(self, pose):
        kps = pose.keypoints

        if all(kps[k].score > self.THRESHOLD for k in self.KEYPOINTS):

            e_lelbow_lshoulder = Edge(kps["left elbow"], kps["left shoulder"])
            e_lelbow_lwrist = Edge(kps["left elbow"], kps["left wrist"])
            e_relbow_rshoulder = Edge(kps["right elbow"], kps["right shoulder"])
            e_relbow_rwrist = Edge(kps["right elbow"], kps["right wrist"])
            e_lshoulder_rshoulder = Edge(kps["left shoulder"], kps["right shoulder"])

            j_lelbow = Joint(e_lelbow_lshoulder, e_lelbow_lwrist)
            j_relbow = Joint(e_relbow_rshoulder, e_relbow_rwrist)
            j_lshoulder = Joint(e_lshoulder_rshoulder, ~e_lelbow_lshoulder)
            j_rshoulder = Joint(~e_lshoulder_rshoulder, ~e_relbow_rshoulder)

            return {
                "j_lelbow_angle": j_lelbow.angle,
                "j_relbow_angle": j_relbow.angle,
                "j_lshoulder_angle": j_lshoulder.angle,
                "j_rshoulder_angle": j_rshoulder.angle,
            }
        else:
            return None

    def get_state(self, stats):
        if stats is not None:
            if (
                stats["j_lelbow_angle"] >= 150
                and stats["j_relbow_angle"] >= 150
                and stats["j_lshoulder_angle"] <= 120
                and stats["j_rshoulder_angle"] <= 120
            ):
                return 1
            elif (
                stats["j_lelbow_angle"] <= 100
                and stats["j_relbow_angle"] <= 100
                and stats["j_lshoulder_angle"] >= 150
                and stats["j_rshoulder_angle"] >= 150
            ):
                return 2
            else:
                return 0
        else:
            return 0


WORKOUTS = {"toe_tap": ToeTap, "jumping_jacks": JumpingJacks, "push_up": PushUp}
