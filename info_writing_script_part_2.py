# Camera Communication Video for Crosswalk Project
# Author: Donavin S.
# Reviewer: Kody R.
# 8-14-2026

import time
import cv2
import os
import csv
import sqlite3

# Use datetime module to get the current date and time of frames (images) from the camera
from datetime import datetime

#from ultralytics import YOLO

from openpyxl import load_workbook

# The YOLO .pt is a file that contains the model weights used for detecting objects, such as a person, a phone, or distance.
#model = YOLO("yolo26n.pt")

# Will be used in the count of population density in the picture that is caputured ("Saved_Capture")
#person = 0

# Remember capital letter first with boolean values.
#phone_present = False


# Open the camera
# If I want to have it support a USB connection, change the 0 to a 1 or 2 depending on how many cameras are connected to the computer.
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

    #for i in range(screen_shot_num):
    # Read each frame from the camera
    ret, frame = camera_feed.read()

    if not ret:
      print("Failed to capture 10 second interval from camera.")
      break

     
    # Write each frame that correctly outputs to the mp4 video file.
    output.write(frame)

    #WRITE A STATEMENT FOR LOOP HERE FOR S TO BE PRESSED ATLEAST 5 TIMES
    #This if statement captures the current date and time for when a picture is captured after pressing "c".

    #screen_shot_num = 5

  
    #Make this if statement inside the while loop for more than one picture to be taken.
    if cv2.waitKey(1) & 0xFF == ord('s'):

      time_date = datetime.now()
      #.strftime("%Y-%m-%d %H:%M:%S")

      time_text = time_date.strftime("%Y-%m-%d %H:%M:%S")
    
      #Make sure live feed does not get tampered with.
      save_capture = frame.copy()

      cv2.putText(save_capture, time_text, (10, save_capture.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
      file_name =  time_date.strftime("photo_%m-%d-%Y_%H-%M-%S{i + 1}.jpg")

      cv2.imwrite(file_name, save_capture)

      file_name = file_name

      video_file_path = capture_feed_path

      img_file_path = "C:\\Users\\donav\\CROSS-Crosswalk-Recognition-and-Obstruction-Safety-System-\\CROSS-Crosswalk-Recognition-and-Obstruction-Safety-System-" + file_name

      #screen_shot_num += 1
      
            

      print(f"Saved {file_name}")


      #results = model("file_name.jpg")

    # Defining a result of a person detected with result, figured out from the image from the results variable, with the ultralytics YOLO model.
    #for result in results:
      
      #for box in result.boxes:

        # Two objects to define the person in a box.
        #class_id = int(box.cls[0])
        #class_name = model.names[class_id]

        # If a person is found from the dimensions (id, and name), then person is detected.
        #if class_name == "person":

          # Increment count of person.
          #person += 1

    # Defining a result of a person detected with result, figured out from the image from the results variable, with the ultralytics YOLO model.
    #for result in results:
          
      #for box in result.boxes:
    
        # Two objects to define the person in a box.
        #class_id = int(box.cls[0])
        #confidence = float(box.conf[0])

        #if result.names[class_id] == "cell phone" and confidence > 0.5:
          #phone_present = True


      break




id = 1



  # I want to then open a .csv file to store the date and time of the image captured.
  # First, open a .csv file that is ready to be written in.
  # Then, write the row of the first image caputured to it.
#with open("offender_registery.xlsx", mode='a', newline='') as file:

    # File is a csv type to write with.
    #writer = csv.writer(file)

    #writer.writerow(["ID", "File_Name", "Date_Time"])
    #writer.writerow([id, file_name, time_text])

    #for i in range(1):
      #writer.writerow([id, file_name, time_text])
      #id += 1

      #if(id > 1):
        #id += id

    
#Load the workbook in the excel file.
wb = load_workbook("offender_registery.xlsx")

# Define the sheet name.
sheet_name = "Sheet1"

#Load the worksheet.
ws = wb[sheet_name] if sheet_name in wb.sheetnames else wb.active

ws.append([id, file_name, time_text, video_file_path, img_file_path])
#ws.append([id, file_name, time_text, video_file_path, img_file_path, person])
#ws.append([id, file_name, time_text, video_file_path, img_file_path, person, phone_present])

wb.save("offender_registery.xlsx")






# Release the camera and close the window.
camera_feed.release()

# This is for the 10 second interval release.
output.release()

#print("Current working directory:")
#print(os.getcwd())
cv2.destroyAllWindows() 