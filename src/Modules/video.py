import cv2 
import os

vid = cv2.VideoCapture(0)
out = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (1280, 720))
while(True): 
      
    # Capture the video frame 
    # by frame 
    ret, frame = vid.read() 
    out.write(frame)
  
    # Display the resulting frame 
    cv2.imshow('frame', frame) 
      
    # the 'q' button is set as the 
    # quitting button you may use any 
    # desired button of your choice 
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break


vid.release() 
out.release()
# Destroy all the windows 
cv2.destroyAllWindows() 
