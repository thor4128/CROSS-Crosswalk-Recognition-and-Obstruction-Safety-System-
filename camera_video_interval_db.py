# Camera Communication Video for Crosswalk Project
# Author: Donavin S.
# Reviewer: Kody R.
# 9-1-2026
import time
import cv2
import os
import csv
import sqlite3

# Need a database path in order to connect to the database.
# Prevents database interpreting special characters as backlashes (which would make for incorrect database path).
db_path = r"C:/Users/donav/Documents/test_info.db"

# Connect to the sqlite3 database called (test_info).
db_connection = sqlite3.connect(db_path)

# Create the cursor to execute data base commands within the database.
db_cursor = db_connection.cursor()

#Use datetime module to get the current date and time of frames (images) from the camera
from datetime import datetime

# Use this library to create a link to folder where the video is saved.
from pathlib import Path

# Open the camera
#If I want to have it support a USB connection, change the 0 to a 1 or 2 depending on how many cameras are connected to the computer.
#camera_feed = cv2.VideoCapture(1, cv2.CAP_DSHOW)
camera_feed = cv2.VideoCapture(0, cv2.CAP_DSHOW)

# This while loop is for the continuous camera video and for the pop up window of it while it is going.
while True:

  # Read each frame from the camera
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


  # While the timer is running for the 10 seconds,
  while time.time() - start < 10:

    # Read each frame from the camera
    ret, frame = camera_feed.read()

    if not ret:
      print("Failed to capture 10 second interval from camera.")
      break

     
    # Write each frame that correctly outputs to the mp4 video file.
    output.write(frame)


  #id = 1

    #This if statement captures the current date and time for when a picture is captured after pressing "c".
  if cv2.waitKey(1) & 0xFF == ord('s'):

    time_date = datetime.now()
    #.strftime("%Y-%m-%d %H:%M:%S")

    time_text = time_date.strftime("%Y-%m-%d %H:%M:%S")
    
    #Make sure live feed does not get tampered with.
    save_capture = frame.copy()

    cv2.putText(save_capture, time_text, (10, save_capture.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Object "file_name" is the .jpg file that is saved as the image.
    file_name =  time_date.strftime("license_plate_photo_%m-%d-%Y_%H-%M-%S.jpg")

    # Save the image to the captured_plates folder. This is the directory for the captured images.
    cv2.imwrite(file_name, save_capture)

    # This places the captured image into the captured_plates folder.
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

  # This turns the video file path into a link to access the video.
  capture_feed_path_link = Path(capture_feed_path).as_uri()

  # Here, is where a query for the database can be executed, since the video above the interval is captured already.
  # This is where the database has to be updated.
  #db_cursor.execute("""INSERT INTO registry_of_offenders (time, video_file_path) Values (?, ?)""", (datetime.now(), capture_feed_path))
  db_cursor.execute("""INSERT INTO registry_of_offenders (time, video_file_path) Values (?, ?)""", (datetime.now(), capture_feed_path_link))
  
 
 # Commit the changes to the database (save the changes).
  db_connection.commit()

  # Close the database connection once changes are made.
  db_connection.close()

  # Delete the Open CV window(s) from the camera feed, so the code is at a "clear" or "complete" state.
  cv2.destroyAllWindows() 