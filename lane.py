import tkinter as tk
from tkinter import Label
import cv2
from PIL import Image, ImageTk
import numpy as np

def start_camera(camera_index=0):
    def process_frame(frame):
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # Edge detection using Canny
        edges = cv2.Canny(blur, 50, 150)
        
        # Define the region of interest
        height, width = edges.shape
        mask = np.zeros_like(edges)
        polygon = np.array([[
            (0, height), (width, height), (width//2, height//2)
        ]], np.int32)
        cv2.fillPoly(mask, polygon, 255)
        cropped_edges = cv2.bitwise_and(edges, mask)

        # Hough Line Transform for detecting lanes
        lines = cv2.HoughLinesP(cropped_edges, 1, np.pi/180, 50, minLineLength=40, maxLineGap=150)
        line_image = np.zeros_like(frame)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(line_image, (x1, y1), (x2, y2), (0, 255, 0), 5)
        
        # Overlay detected lanes onto the original frame
        combined = cv2.addWeighted(frame, 0.8, line_image, 1, 1)
        return combined

    def update_frame():
        ret, frame = cap.read()
        if ret:
            processed_frame = process_frame(frame)
            show_frame(processed_frame)
            video_label.after(10, update_frame)
        else:
            # Stop if the camera feed is unavailable
            cap.release()

    def show_frame(frame):
        # Convert the frame for displaying in Tkinter
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    # Attempt to open the selected camera index
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Camera at index {camera_index} not found.")
        return
    update_frame()

# GUI setup
root = tk.Tk()
root.title("Real-Time Lane Detection System")
root.geometry("800x600")

# Video display area
video_label = Label(root)
video_label.pack()

# Try default camera (0), fallback to USB camera (1) if default is not available
if cv2.VideoCapture(0).isOpened():
    start_camera(0)  # Default camera
elif cv2.VideoCapture(1).isOpened():
    start_camera(1)  # USB/mobile camera
else:
    print("No camera detected. Please connect a camera and try again.")

root.mainloop()
