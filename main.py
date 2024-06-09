import tkinter as tk
from tkinter import filedialog
import cv2
import subprocess
from PIL import Image, ImageTk


def run_ffmpeg_command():
    overlay_x = overlay_label.winfo_x()
    overlay_y = overlay_label.winfo_y()
    crop_left = left_entry.get()
    crop_right = right_entry.get()
    crop_top = top_entry.get()
    crop_bottom = bottom_entry.get()
    output_file = output_entry.get()
    command = f'ffmpeg -i {bg_path} -i {overlay_path} -filter_complex "[1:v] crop=iw-({crop_left}+{crop_right}):ih-({crop_top}+{crop_bottom}):{crop_left}:{crop_top} [cropped]; [0:v][cropped] overlay={overlay_x}:{overlay_y}" -pix_fmt yuv420p -c:a copy {output_file}'
    subprocess.run(command, shell=True)


def update_overlay_position(event):
    if overlay_label.winfo_containing(event.x_root, event.y_root) == overlay_label:
        overlay_label.place(x=overlay_label.winfo_x() + event.x - overlay_label.winfo_width() // 2,
                            y=overlay_label.winfo_y() + event.y - overlay_label.winfo_height() // 2)


def update_crop_preview(event):
    crop_left = int(left_entry.get())
    crop_right = int(right_entry.get())
    crop_top = int(top_entry.get())
    crop_bottom = int(bottom_entry.get())
    cropped_frame = overlay_frame[crop_top:overlay_frame.shape[0] -
                                  crop_bottom, crop_left:overlay_frame.shape[1]-crop_right]
    cropped_frame = cv2.resize(
        cropped_frame, (overlay_frame.shape[1], overlay_frame.shape[0]))
    cropped_image = Image.fromarray(cropped_frame)
    cropped_photo = ImageTk.PhotoImage(cropped_image)
    overlay_label.configure(image=cropped_photo)
    overlay_label.image = cropped_photo


def update_video_frames():
    global overlay_frame
    ret, overlay_frame = overlay_video.read()
    if not ret:
        overlay_video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        _, overlay_frame = overlay_video.read()
    overlay_frame = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)
    update_crop_preview(None)

    window.after(30, update_video_frames)


def select_background():
    global bg_path, bg_image, bg_photo
    bg_path = filedialog.askopenfilename(
        filetypes=[("All Files", "*.*"), ("Image Files", "*.png;*.jpg;*.jpeg")])
    if bg_path:
        bg_image = cv2.imread(bg_path)
        bg_image = cv2.cvtColor(bg_image, cv2.COLOR_BGR2RGB)
        bg_photo = ImageTk.PhotoImage(Image.fromarray(bg_image))
        bg_label.configure(image=bg_photo)


def select_overlay():
    global overlay_path, overlay_video, overlay_frame
    overlay_path = filedialog.askopenfilename(
        filetypes=[("All Files", "*.*"), ("Video Files", "*.mp4;*.mkv;*.avi")])
    if overlay_path:
        overlay_video = cv2.VideoCapture(overlay_path)
        _, overlay_frame = overlay_video.read()
        overlay_frame = cv2.cvtColor(overlay_frame, cv2.COLOR_BGR2RGB)
        update_crop_preview(None)


# Create the main window
window = tk.Tk()
window.title("Overlay Position")
window.configure(bg="#222222")

# Create buttons to select background and overlay files
bg_button = tk.Button(window, text="Select Background", command=select_background,
                      bg="#333333", fg="white", activebackground="#444444", activeforeground="white")
bg_button.pack(pady=5)

overlay_button = tk.Button(window, text="Select Overlay", command=select_overlay,
                           bg="#333333", fg="white", activebackground="#444444", activeforeground="white")
overlay_button.pack(pady=5)

# Create a label to display the background image
bg_label = tk.Label(window, bg="#222222")
bg_label.pack()

# Create a label to represent the overlay
overlay_label = tk.Label(window, cursor="fleur", bg="#222222")
overlay_label.place(x=0, y=0)

# Bind the mouse motion event to update the overlay position
overlay_label.bind("<B1-Motion>", update_overlay_position)

# Create a frame for crop entries
crop_frame = tk.Frame(window, bg="#222222")
crop_frame.pack()

output_frame = tk.Frame(window, bg="#222222")
output_frame.pack(pady=10)

output_label = tk.Label(
    output_frame, text="Output File Name:", fg="white", bg="#222222")
output_label.pack(side=tk.LEFT)

output_entry = tk.Entry(output_frame, bg="#333333",
                        fg="white", insertbackground="white")
output_entry.pack(side=tk.LEFT)
output_entry.insert(0, "output.mp4")

# Create entry fields for crop values
left_label = tk.Label(crop_frame, text="Left:", fg="white", bg="#222222")
left_label.grid(row=0, column=0)
left_entry = tk.Entry(crop_frame, bg="#333333",
                      fg="white", insertbackground="white")
left_entry.grid(row=0, column=1)
left_entry.insert(0, "0")

right_label = tk.Label(crop_frame, text="Right:", fg="white", bg="#222222")
right_label.grid(row=0, column=2)
right_entry = tk.Entry(crop_frame, bg="#333333",
                       fg="white", insertbackground="white")
right_entry.grid(row=0, column=3)
right_entry.insert(0, "0")

top_label = tk.Label(crop_frame, text="Top:", fg="white", bg="#222222")
top_label.grid(row=1, column=0)
top_entry = tk.Entry(crop_frame, bg="#333333",
                     fg="white", insertbackground="white")
top_entry.grid(row=1, column=1)
top_entry.insert(0, "0")

bottom_label = tk.Label(crop_frame, text="Bottom:", fg="white", bg="#222222")
bottom_label.grid(row=1, column=2)
bottom_entry = tk.Entry(crop_frame, bg="#333333",
                        fg="white", insertbackground="white")
bottom_entry.grid(row=1, column=3)
bottom_entry.insert(0, "0")

# Bind the entry fields to update the crop preview
left_entry.bind("<KeyRelease>", update_crop_preview)
right_entry.bind("<KeyRelease>", update_crop_preview)
top_entry.bind("<KeyRelease>", update_crop_preview)
bottom_entry.bind("<KeyRelease>", update_crop_preview)

# Create a button to run the FFmpeg command
run_button = tk.Button(window, text="Run FFmpeg Command", command=run_ffmpeg_command,
                       bg="#333333", fg="white", activebackground="#444444", activeforeground="white")
run_button.pack(pady=10)

# Start the GUI main loop
window.mainloop()
