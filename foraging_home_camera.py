
import picamera


camera = picamera.PiCamera()
camera.resolution = (1024,768)
camera.framerate = 10
camera.start_recording('testvideo.h264')
camera.wait_recording(600)
camera.stop_recording()
camera.close()








