# Camera Communication Video for Crosswalk Project
# Author: Donavin S.
# Reviewer: Kody R.
# 7-17-2026
import time
import cv2
import os
import csv
import sqlite3
#cx = sqlite3.connect("test.db")
#cx = sqlite3.connect(":memory:")

#cu = cx.cursor()  
  
# create a table  
#cu.execute("create table lang(name, first_appeared)")  

# insert values into a table  
#cu.execute("insert into lang values (?, ?)", ("C", 1972))  
  
# execute a query and iterate over the result  
#for row in cu.execute("select * from lang"):  
 # print(row)  
  
 # cx.close()

#print("Current working directory:", os.getcwd())
#print("Script location:", os.path.dirname(os.path.abspath(__file__)))

#Use datetime module to get the current date and time of frames (images) from the camera
from datetime import datetime

# Open the camera
#If I want to have it support a USB connection, change the 0 to a 1 or 2 depending on how many cameras are connected to the computer.
#camera_feed = cv2.VideoCapture(1, cv2.CAP_DSHOW)
camera_feed = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# This while loop is for the continuous camera video and for the pop up window of it while it is going.
while True:

  ret, frame = camera_feed.read()

  if not ret:
    break

  # Display the camera feed picture
  cv2.imshow('Live Camera Feed', frame)

  
  # Need to get the frames per second, and dimensions of the camera frame for the video feed.
  # 10 fps is standard for laptop testing, but for a better camera, use 30 or 60 fps.
  #fps = int(camera_feed.get(cv2.CAP_PROP_FPS))
  fps = 10
  width = int(camera_feed.get(cv2.CAP_PROP_FRAME_WIDTH))
  height = int(camera_feed.get(cv2.CAP_PROP_FRAME_HEIGHT))

  print("Camera opened:", camera_feed.isOpened())

  #Put a current date of when folder was created (other 10 second video feeds will have a new folder under a new date).
  capture_feed = datetime.now().strftime("capture_feed_%m-%d-%Y_%H-%M-%S")

  #Make the folder/directory for the video, if the name of the folder exists, it can still work.
  os.makedirs(capture_feed, exist_ok = True)

  #The path of the folder needs to join with the filename along with the tyle of file.
  capture_feed_path = os.path.join(capture_feed, "video.mp4")


  #This is the output of what the video shows.
  output = cv2.VideoWriter(capture_feed_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

  # Start timer for the video interval of 10 seconds.
  start = time.time()


    #frame_number = 0;

  # While the timer is running for the 10 seconds,
  while time.time() - start < 10:

    # Read each frame from the camera
    ret, frame = camera_feed.read()

    if not ret:
      print("Failed to capture 10 second interval from camera.")
      break

     
    # Write each frame that correctly outputs to the mp4 video file.
    output.write(frame)

    #This if statement captures the current date and time for when a picture is captured after pressing "c".
  if cv2.waitKey(1) & 0xFF == ord('s'):

    time_date = datetime.now()
    #.strftime("%Y-%m-%d %H:%M:%S")

    time_text = time_date.strftime("%Y-%m-%d %H:%M:%S")
    
    #Make sure live feed does not get tampered with.
    save_capture = frame.copy()

    cv2.putText(save_capture, time_text, (10, save_capture.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
    file_name =  time_date.strftime("license_plate_photo_%m-%d-%Y_%H-%M-%S.jpg")

    cv2.imwrite(file_name, save_capture)

    file_name = "captured_plates/" + file_name

    print(f"Saved {file_name}")

    break

    # Testing number of frames per second.
    #frame_number += 1
    #print(f"Frame number:  {frame_number}")

    #Exit the camera feed loop when q is pressed.
    # if cv2.waitKey(1) & 0xFF == ord('q'):
      #  break

  #Release the camera and close the window.
  camera_feed.release()

  #This is for the 10 second interval release.
  output.release()

  #print("Current working directory:")
  #print(os.getcwd())
  cv2.destroyAllWindows() 
