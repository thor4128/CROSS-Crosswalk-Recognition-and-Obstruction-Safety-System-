# Camera Communication for Crosswalk Project
# Author: Donavin S.
# Reviewer: Kody R.

import cv2
import os
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

#Open the camera
#If I want to have it support a USB connection, change the 0 to a 1 or 2 depending on how many cameras are connected to the computer.
#camera_feed = cv2.VideoCapture(1, cv2.CAP_DSHOW)
camera_feed = cv2.VideoCapture(0, cv2.CAP_DSHOW)

print("Camera opened:", camera_feed.isOpened())

while True:

  #Read the camera feed from the laptop
  ret, frame = camera_feed.read()
  #print("ret :", ret)

  if not ret:
    print("Failed to capture frame from camera.")
    break

      
  #Display the camera feed picture
  cv2.imshow('Live Camera Feed', frame)

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

    

   # import os
  #  save_dir = "captured_plates"
  #  os.makedirs(save_dir, exist_ok=True)

   # filename = os.path.join(save_dir, "license_plate_photo_%m-%d-%Y_%H-%M-%S.jpg")
   # cv2.imwrite(filename, frame)  

  


  #Exit the camera feed loop when q is pressed.
  if cv2.waitKey(1) & 0xFF == ord('q'):
    break

#Release the camera and close the window.
camera_feed.release()
#print("Current working directory:")
#print(os.getcwd())
cv2.destroyAllWindows()

    






