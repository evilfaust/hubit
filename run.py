import cv2
import sys
from em_model import EMR
import numpy as np
import imutils


EMOTIONS = ['angry', 'disgusted', 'fearful', 'happy', 'sad', 'surprised', 'neutral']
cascade_classifier = cv2.CascadeClassifier('haarcascade_files/haarcascade_frontalface_default.xml')

def brighten(data,b):
     datab = data * b
     return datab    

def format_image(image):
  if image is None:
    cv2.destroyAllWindows()
    exit()
  if len(image.shape) > 2 and image.shape[2] == 3:
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  else:
    image = cv2.imdecode(image, cv2.CV_LOAD_IMAGE_GRAYSCALE)
  faces = cascade_classifier.detectMultiScale(
      image,
      scaleFactor = 1.3 ,
      minNeighbors = 5
  )
  if not len(faces) > 0:
    return None
  max_area_face = faces[0]
  for face in faces:
    if face[2] * face[3] > max_area_face[2] * max_area_face[3]:
      max_area_face = face
  face = max_area_face
  image = image[face[1]:(face[1] + face[2]), face[0]:(face[0] + face[3])]
  try:
    image = cv2.resize(image, (48,48), interpolation = cv2.INTER_CUBIC) / 255
  except Exception:
    print("[+] Problem during resize")
    return None
  return image

network = EMR()
network.build_network()

video_capture = cv2.VideoCapture('test.mp4')
_, frame = video_capture.read()
(w, h, c) = frame.shape
font = cv2.FONT_HERSHEY_SIMPLEX

feelings_faces = []
for index, emotion in enumerate(EMOTIONS):
  feelings_faces.append(cv2.imread('./emojis/' + emotion + '.png', -1))

i = False
while True:
  ret, frame = video_capture.read()
  result = network.predict(format_image(frame))
  if result is not None:
    for index, emotion in enumerate(EMOTIONS):
      cv2.putText(frame, emotion, (10, index * 20 + 20), cv2.FONT_HERSHEY_PLAIN, 0.5, (0, 255, 0), 1);
      cv2.rectangle(frame, (130, index * 20 + 10), (130 + int(result[0][index] * 100), (index + 1) * 20 + 4), (255, 0, 0), -1)
    
    arr = list(result[0])
    face_image = feelings_faces[arr.index(max(arr))]
    for c in range(0, 3):
      frame[200:320, 10:130, c] = face_image[:,:,c] * (face_image[:, :, 3] / 255.0) +  frame[200:320, 10:130, c] * (1.0 - face_image[:, :, 3] / 255.0)
  
  cv2.imshow('HUBIT', imutils.resize(frame, width=w // 4, height=h // 4))
  if 0xFF == ord('q') & cv2.waitKey(1):
    break



#video_capture = cv2.resize(video_capture, fx=0.5, fy=0.5, interpolation = cv2.INTER_CUBIC)
#video_capture = imutils.resize(video_capture, width=400)
video_capture.release()
cv2.destroyAllWindows()
exit()
