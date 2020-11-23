# HIIT PI

HIIT PI is a [Dash](https://dash.plot.ly/) app that uses machine learning (specifically pose estimation) on edge devices to help track your [HIIT](https://en.wikipedia.org/wiki/High-intensity_interval_training) workout progress in real time (~30fps). The backend runs everything locally on a [Raspberry Pi](https://www.raspberrypi.org/) while you interact with the app wherever there is a web browser connecting to the same local network as the Pi does.

## How it works
* [Video demo](https://youtu.be/eErfWulipiA)
* [Blog post](https://iamjameswong.com/2020-04-06-building-a-home-hiit-workout-trainer/)

## Hardwares
* [Raspberry Pi](https://www.raspberrypi.org/products/raspberry-pi-4-model-b/) *(Pi 4 recommended)*
* [Raspberry Pi Camera Module v2](https://www.raspberrypi.org/products/camera-module-v2/)
* [Google's Coral USB Accelerator](https://coral.ai/products/accelerator/) (Edge TPU)

## Softwares
* [Raspbian 10 Buster](https://www.raspberrypi.org/downloads/raspbian/)
* [Docker](https://docs.docker.com/engine/install/debian/) & [Docker Compose](https://docs.docker.com/compose/install/)
* [Python 3.7+](https://www.python.org/)

## Usage
1. SSH into your Raspberry Pi and clone the repository.
2. Install Docker & Docker Compose.
3. Build our Docker images and spawn up the containers with
   ```
   $ docker-compose -d --build up 
   ```
4. *(Optional)* For maximum performance, swap the standard Edge TPU runtime library `libedgetpu1-legacy-std` with `libedgetpu1-legacy-max`  
   1. get into the shell of container `web-hiitpi` by  
      ```
      $ docker exec -it web-hiitpi bash
      ``` 
   2. run the following inside the container  
      ```
      $ DEBIAN_FRONTEND=dialog apt-get install -y libedgetpu1-legacy-max
      ```
      *Note: select `yes` and hit `ENTER` in the interactive installation process.*  
   3. restart the `web` service after the above install finishes  
      ```
      $ docker-compose restart web 
      ```
    
5. Go to `<your_pis_ip_address>:8050` on a device in the same LAN as the Pi's, and then enter a player name in the welcome page to get started.
6. The live-updating line graphs show the model inferencing time (~50fps) and pose score frame by frame, which indicates how likely the camera senses a person in front.
7. Selecting a workout from the dropdown menu starts a training session, where your training session stats (`reps` & `pace`) are updating in the widgets below as the workout progresses. Tap the `DONE!` button to complete the session, or `EXIT?` to switch a player. Click `LEADERBOARD` to view total reps accomplished by top players.

## Notes
* This project currently has implemented a couple of workouts to play with, and we're planning to expand our workout repertoire as it evolves over time.