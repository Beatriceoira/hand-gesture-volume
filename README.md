# Hand Gesture Volume Controller

A real-time computer vision application that uses **hand gestures to control system audio volume**. The application tracks the user's hand through a webcam using **MediaPipe Hand Landmarker**, measures the distance between the thumb and index finger, and maps that distance to the system's master volume.

The project is designed for **Linux systems using PulseAudio/PipeWire's PulseAudio compatibility layer**.

## Features

* Real-time webcam hand tracking
* MediaPipe hand landmark detection
* Tracks thumb and index finger positions
* Calculates the distance between fingertips
* Converts finger distance into system volume
* Displays a visual volume bar
* Displays volume percentage in real time
* Draws the detected hand skeleton
* Visual feedback when fingertips are close together
* Real-time processing using OpenCV
* Linux audio control through `pulsectl`

## How It Works

The application uses the distance between two hand landmarks:

* **Landmark 4** → Thumb tip
* **Landmark 8** → Index finger tip

The Euclidean distance between these points is calculated:

```text
distance = √((x₂ - x₁)² + (y₂ - y₁)²)
```

That distance is then mapped to a volume range:

```text
50 pixels  → 0% volume
220 pixels → 100% volume
```

Conceptually:

```text
       Thumb
         ●
          \
           \  ← Distance controls volume
            \
             ●
          Index Finger

       Small distance
             ↓
          Low volume

       Large distance
             ↓
         High volume
```

The resulting value is sent to the system audio sink using `pulsectl`.

## Architecture

```text
┌──────────────┐
│    Webcam    │
└──────┬───────┘
       │
       ▼
┌────────────────────┐
│      OpenCV        │
│ Capture Video      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│    MediaPipe       │
│ Hand Landmarker    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Hand Landmarks     │
│ Thumb + Index      │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Distance           │
│ Calculation        │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ NumPy Interpolation│
│ Distance → Volume  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│     pulsectl       │
│ System Audio       │
└────────────────────┘
```

## Technologies

| Technology                | Purpose                              |
| ------------------------- | ------------------------------------ |
| Python                    | Main programming language            |
| OpenCV                    | Webcam capture and visualization     |
| MediaPipe                 | Hand landmark detection and tracking |
| NumPy                     | Volume interpolation                 |
| pulsectl                  | Linux system audio control           |
| PulseAudio / PipeWire     | Audio subsystem                      |
| MediaPipe Hand Landmarker | Hand pose estimation                 |

## Project Structure

```text
hand-gesture-volume/
├── handgesture.py
├── hand_landmarker.task
├── requirements.txt
├── README.md
└── .gitignore
```

### Files

#### `activity.py`

Main application containing:

* Webcam initialization
* MediaPipe configuration
* Hand landmark detection
* Finger distance calculation
* Volume interpolation
* PulseAudio volume control
* OpenCV visualization

#### `hand_landmarker.task`

The MediaPipe Hand Landmarker model used for detecting hand landmarks.

> The model file is required for the application to run.

#### `requirements.txt`

Python dependencies required by the application.

## 📋 Requirements

### Hardware

* Linux computer
* Webcam
* Working audio output device

### Software

* Python 3.x
* OpenCV
* NumPy
* MediaPipe
* pulsectl
* PulseAudio or PipeWire with PulseAudio compatibility

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/hand-gesture-volume.git
cd hand-gesture-volume
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```text
opencv-python
numpy
mediapipe
pulsectl
```

### 4. Install Linux audio dependencies

On Ubuntu/Debian-based systems:

```bash
sudo apt install pulseaudio-utils
```

If your system uses PipeWire, make sure its PulseAudio compatibility layer is available.

You can check available audio sinks with:

```bash
pactl list short sinks
```

## 📦 MediaPipe Model

The application expects:

```text
hand_landmarker.task
```

in the project directory.

The model path is configured here:

```python
model_path = "hand_landmarker.task"
```

If you store the model somewhere else, update this path accordingly.

## ▶️ Running the Application

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Then run:

```bash
python3 activity.py
```

A webcam window should appear:

```text
handDetector
```

Place your hand in front of the camera.

### Gesture Controls

```text
🤏 Fingers close
       ↓
   Low volume

🤌 Fingers apart
       ↓
  Higher volume
```

Not the whole hand!!! You just need to do pinching using your thumb and index!

The distance between your thumb and index finger directly controls the system volume.

### Exit

Press:

```text
Q
```

to close the application.

## 🎮 Gesture Mapping

The current implementation uses the following mapping:

| Finger Distance | Volume |
| --------------: | -----: |
|       `< 50 px` |    ~0% |
|         `50 px` |     0% |
|        `100 px` |   ~26% |
|        `150 px` |   ~53% |
|        `220 px` |   100% |
|      `> 220 px` |   100% |

The mapping is performed using NumPy:

```python
vol = np.interp(
    length,
    [50, 220],
    [minVol, maxVol]
)
```

The displayed volume percentage uses:

```python
volPer = np.interp(
    length,
    [50, 220],
    [0, 100]
)
```

## 🖥️ Webcam Configuration

The application currently uses camera index `1`:

```python
cam = cv2.VideoCapture(1)
```

and requests a resolution of:

```text
640 × 480
```

If your webcam is not detected, try:

```python
cam = cv2.VideoCapture(0)
```

Common camera indexes are:

```text
0 → Built-in/default webcam
1 → Secondary webcam
2 → Additional camera
```

## Audio Sink Selection

The application currently selects the first available PulseAudio sink:

```python
sink = pulse.sink_list()[0]
```

This means the first detected audio output is automatically selected.

To inspect your available sinks:

```bash
pactl list short sinks
```

For a more advanced implementation, the application could allow the user to explicitly select an audio device.

## MediaPipe Hand Tracking

The application detects one hand:

```python
num_hands=1
```

with:

```python
min_hand_detection_confidence=0.5
min_tracking_confidence=0.5
```

MediaPipe provides 21 hand landmarks.

The application specifically uses:

```text
Landmark 4 → Thumb tip
Landmark 8 → Index finger tip
```

The detected coordinates are converted from normalized MediaPipe coordinates into webcam pixel coordinates:

```python
cx = int(lm.x * w)
cy = int(lm.y * h)
```

## 📊 Visual Feedback

The application displays:

### Hand skeleton

MediaPipe hand connections are drawn directly onto the webcam frame.

### Finger indicators

The thumb and index fingertips are highlighted:

```text
○ Thumb
│
│
○ Index
```

### Connection line

A line is drawn between the fingertips.

It changes from green to red when the fingers are very close:

```text
Normal:

Thumb ●────────● Index
       Green


Very close:

Thumb ●● Index
      Red
```

### Volume meter

A vertical volume bar is displayed on the left side of the camera window.

```text
┌───┐
│███│
│███│
│███│
│██ │
│   │
│   │
└───┘
 65%
```

## Configuration

Several parameters can be adjusted directly in `activity.py`.

### Camera resolution

```python
wCam, hCam = 640, 480
```

For example:

```python
wCam, hCam = 1280, 720
```

### Camera device

```python
cam = cv2.VideoCapture(1)
```

Change `1` to the appropriate camera index.

### Minimum gesture distance

```python
[50, 220]
```

The first value represents the minimum useful distance.

### Maximum gesture distance

```python
[50, 220]
```

The second value represents the distance corresponding to maximum volume.

### Hand detection confidence

```python
min_hand_detection_confidence=0.5
```

### Hand tracking confidence

```python
min_tracking_confidence=0.5
```

## Troubleshooting

### Camera does not open

Try another camera index:

```python
cam = cv2.VideoCapture(0)
```

You can also inspect available video devices:

```bash
ls /dev/video*
```

### `hand_landmarker.task` not found

Make sure the model exists in the project directory:

```bash
ls
```

You should see:

```text
activity.py
hand_landmarker.task
```

Alternatively, provide an absolute or relative path to the model.

### No audio changes

Check available sinks:

```bash
pactl list short sinks
```

Then verify that PulseAudio/PipeWire is running.

For PipeWire systems:

```bash
systemctl --user status pipewire
systemctl --user status pipewire-pulse
```

### Wrong audio device is controlled

The current implementation uses:

```python
pulse.sink_list()[0]
```

which selects the first sink returned by PulseAudio.

A future version can select a sink by name instead.

### MediaPipe import/model errors

Make sure the virtual environment is active:

```bash
source .venv/bin/activate
```

Then verify:

```bash
python3 --version
pip show mediapipe
```

## Permissions

Depending on the Linux distribution and desktop environment, the webcam may require permission.

Check available video devices:

```bash
ls -l /dev/video*
```

If your user cannot access the webcam, check membership in the `video` group:

```bash
groups
```

On systems where appropriate:

```bash
sudo usermod -aG video $USER
```

Log out and back in afterward.

## Limitations

The current version has several intentional simplifications:

* Only one hand is tracked.
* The first PulseAudio sink is automatically selected.
* Camera index is hard-coded.
* Gesture calibration is fixed.
* Volume changes are applied continuously.
* There is no smoothing/filtering of the measured distance.
* There is no GUI configuration panel.
* No gesture customization is available.
* The application is primarily designed for Linux audio systems.

## Future Improvements

Potential improvements include:

### Volume smoothing

Apply a moving average or exponential smoothing filter to prevent rapid volume fluctuations.

```text
Raw distance
     ↓
Smoothing filter
     ↓
Stable volume
```

### Dynamic calibration

Allow the user to define:

```text
Minimum gesture distance
Maximum gesture distance
Minimum volume
Maximum volume
```

at runtime.

### Audio device selection

Allow users to select:

```text
Built-in Speakers
USB Headset
Bluetooth Headphones
HDMI Output
```

instead of always using the first sink.

### Multiple gestures

Additional gestures could control other media functions:

```text
Pinch       → Volume
Open palm   → Play/Pause
Thumb up    → Next track
Thumb down  → Previous track
Fist        → Mute
```

### Mute gesture

A fist or specific gesture could toggle system mute.

### Media controls

Integrate with Linux media players to provide:

* Play
* Pause
* Next
* Previous
* Mute
* Volume control

### Desktop GUI

Build a graphical interface for:

* Camera selection
* Audio device selection
* Gesture configuration
* Sensitivity
* Volume range
* Enable/disable gestures

### Gesture visualization

Display additional information:

```text
Hand detected: YES
Distance:      143 px
Volume:        53%
Audio sink:    Speakers
FPS:           30
```

### Performance optimization

Potential optimizations include:

* Frame skipping
* Resolution scaling
* Landmark processing optimization
* Distance smoothing
* CPU/GPU acceleration where supported

## Concepts Demonstrated

This project combines several useful computer science and software engineering concepts:

* Computer vision
* Hand pose estimation
* Machine learning inference
* Real-time video processing
* Coordinate transformation
* Euclidean distance
* Numerical interpolation
* Human-computer interaction
* Linux audio APIs
* Hardware input through webcams
* Real-time visualization
* Python virtual environments

## License

This project is intended for educational and portfolio purposes. Add an appropriate open-source license such as MIT if you plan to distribute it publicly.

## Author

**Beatrice Oira**

Built as a computer vision / human-computer interaction project demonstrating real-time gesture recognition and Linux system integration.
