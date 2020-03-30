# HIIT PI

HIIT PI is a [Dash](https://dash.plot.ly/) app that uses machine learning (specifically pose estiamtion) on edge devices to help track your [HIIT](https://en.wikipedia.org/wiki/High-intensity_interval_training) workout progress in real time (~30fps). The backend runs everything locally on a [Raspberry Pi](https://www.raspberrypi.org/) while you interact with the app wherever there is a web browser connecting to the same local network as the Pi does.

## Previews

## Hardwares
* [Raspberry Pi](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) *(Pi 4 recommended)*
* [Raspberry Pi Camera Module v2](https://www.raspberrypi.org/products/camera-module-v2/)
* [Google's Coral USB Accelerator](https://coral.ai/products/accelerator/) (Edge TPU)

## Softwares
* [Raspbian 10 Buster](https://www.raspberrypi.org/downloads/raspbian/)
* [Python 3.7+](https://www.python.org/)
* [TensorFlow Lite](https://www.tensorflow.org/lite/guide/python)
* [Edge TPU runtime](https://coral.ai/docs/accelerator/get-started/)
* [Dash](https://plotly.com/dash/), [Flask](https://flask.palletsprojects.com/), [Plotly](https://plot.ly/)
* [Redis](https://redis.io/topics/ARM)
* [PiCamera](https://picamera.readthedocs.io/), [OpenCV](https://opencv.org/), ...(more in `requirements.txt`)

## Usage guides
1. SSH into your Raspberry Pi and clone the repository.
2. Set up a working environment with dependencies listed above before running the app by
   ```
   $ python app.py
   ```
3. Go to `<your_pis_ip_address>:8050` on a device in the same LAN as the Pi's, and then enter a player name in the welcome page to get started.
4. The live-updating line graphs show the model inferencing time (~50fps) and pose score frame by frame, which indicates how likely the camera senses a person in front.
5. Selecting a workout from the dropdown menu starts a training session, where your training session stats (`reps` & `pace`) are updating in the widgets below as the workout progresses. Tap the `DONE!` button to complete the session, or `EXIT?` to switch a player. Click `LEADERBOARD` to view total reps accomplished by top players.

## Notes
* This project currently has implemented a couple of workouts to play with, and we're planning to add more later.