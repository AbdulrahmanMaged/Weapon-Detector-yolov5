import tkinter as tk
from tkinter import filedialog
import math
from PIL import Image, ImageTk
import torch
import cv2
#
# # Load the YOLOv5 model
path_to_model = 'E:/Downloads/yolov5/yolov5'
path_to_weights = 'E:/Downloads/yolov5/yolov5/runs/train/exp8/weights/best.pt'
Torch = torch.hub.load(path_to_model, 'custom', path_to_weights)

def image_add_bbox(image, x1, y1, x2, y2,type):
    cropped_image = image[y1:y2, x1:x2]
    if type =='image':
        blurred_image = cv2.GaussianBlur(cropped_image, (13, 13), 0)
        image[y1:y2, x1:x2] = blurred_image
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        return image
    else:
        new_width = 640
        new_height = 480
        blurred_image = cv2.GaussianBlur(cropped_image, (35, 35), 0)
        image[y1:y2, x1:x2] = blurred_image
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        frame = cv2.resize(image, (new_width, new_height))
        cv2.imshow('frame', frame)
        # Exit the loop if the user presses the 'q' key
        if cv2.waitKey(1) == ord('q'):
            frame.release()
            cv2.destroyAllWindows()
            return



def upload_image():
    global file_path, processed_image, detected_object_name
    file_path = filedialog.askopenfilename()
    if file_path:
        frame = cv2.imread(file_path)
        raw_prediction = Torch(frame).pandas().xyxy[0]

        gun_detected = False
        detected_object_name = ""
        for row in raw_prediction.itertuples():
            x1, x2, y1, y2 = (math.ceil(row.xmin)), (math.ceil(row.xmax)), (math.ceil(row.ymin)), (math.ceil(row.ymax))
            label = row.name
            if label == "pistol" or label == "knife":
                gun_detected = True
                detected_object_name = label
                frame = image_add_bbox(frame, x1, y1, x2, y2,type='image')

        processed_image = frame
        display_image(frame, gun_detected, detected_object_name)
def save_image():
    if processed_image is not None and file_path:
       save_file_path = filedialog.asksaveasfilename()
       if save_file_path:
           cv2.imwrite(save_file_path, processed_image)

def upload_video():
    file_path = filedialog.askopenfilename()
    global processed_media
    processed_media = file_path
    if file_path:
        root.withdraw()
        cap = cv2.VideoCapture(file_path)
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            results = Torch(frame)
            bboxes = results.xyxy[0].cpu().numpy()

            for bbox in bboxes:
                x1, y1, x2, y2 = math.ceil(bbox[0]), math.ceil(bbox[1]), math.ceil(bbox[2]), math.ceil(bbox[3])
                image_add_bbox(frame, x1, y1, x2, y2,type='video')
                break

        cap.release()
        root.deiconify()


# def save_video():
#     global file_path, processed_media, is_video
#     if processed_media is not None and file_path and is_video:
#         save_file_path = filedialog.asksaveasfilename()
#         if save_file_path:
#             fourcc = cv2.VideoWriter_fourcc(*'MP4V')
#             out = cv2.VideoWriter(save_file_path, fourcc, 20.0, (640, 480))
#             for frame in processed_media:
#                 out.write(frame)
#             out.release()


def display_image(img, gun_detected, detected_object_name):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img.thumbnail((480, 270))
    img = ImageTk.PhotoImage(img)

    image_label.config(image=img)
    image_label.image = img

    if gun_detected:
        result_label.config(text=f"{detected_object_name.capitalize()} detected.", fg="red")
    else:
        result_label.config(text="No weapon detected.", fg="green")



root = tk.Tk()
root.title("Content Filter")
root.geometry("800x600")

canvas = tk.Canvas(root, width=800, height=600, bg="grey")
canvas.pack(fill="both", expand=True)

title_label = tk.Label(root, text="Content Filter", font=("Arial", 24), bg="grey")
canvas.create_window(400, 70, window=title_label)

description_label = tk.Label(root, text="This program detects knives and pistols in images and videos.", font=("Arial", 14), bg="grey")
canvas.create_window(400, 120, window=description_label)

image_label = tk.Label(root, bg="grey")
canvas.create_window(400, 270, window=image_label)

result_label = tk.Label(root, text="", font=("Arial", 18), bg="grey")
canvas.create_window(400, 420, window=result_label)

button_frame = tk.Frame(root, bg="grey")
canvas.create_window(400, 480, window=button_frame)

upload_image_button = tk.Button(button_frame, text="Upload Image", command=upload_image, bg="#4CAF50", fg="white", font=("Arial", 12))
upload_image_button.pack(side="left", padx=20)

upload_video_button = tk.Button(button_frame, text="Upload Video", command=upload_video, bg="#2196F3", fg="white", font=("Arial", 12))
upload_video_button.pack(side="left", padx=20)

save_image_button = tk.Button(button_frame, text="Save Image", command=save_image, bg="#4CAF50", fg="white", font=("Arial", 12))
save_image_button.pack(side="left", padx=20)

# save_video_button = tk.Button(root, text="Save Video", command=save_video)
# save_video_button.place(relx=0.5, rely=0.9, anchor="center")

file_path = None
processed_image = None
detected_object_name = ""

root.mainloop()
