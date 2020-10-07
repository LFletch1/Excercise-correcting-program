#!usr/bin/env python3
# Lance Fletcher
# August 22, 2020

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import os
import process_video_tools as pvt
# import exercise_analysis_tools as eat
from tkinter import ttk
import time
VIDEO = "None"


def get_video():
    global VIDEO
    VIDEO = filedialog.askopenfilename(initialdir="/", title="Select Video",
                                       filetypes=(("Movie Files", "*.mov"),
                                                  ("AVI Files", "*.avi"),
                                                  ("MP4 Files", "*.mp4")))
    VIDEO = VIDEO.replace("/", "\\")
    global video_label
    video_label.configure(text="Video Selected: \n" + VIDEO)


def process_video():
    start = time.time()
    global VIDEO
    global VAR
    global STR_VAR

    # Error if user has not selected a video
    if VIDEO == "None" or VIDEO == "":
        popup = tk.Tk()
        popup.title('Error')
        popup.geometry('200x100')
        error_label = tk.Label(popup, text='ERROR:\nMust select a video.')
        error_label.pack(padx=10, pady=5)
        close_button = tk.Button(popup, text='Close', command=popup.destroy)
        close_button.pack(padx=10, pady=5)
        popup.mainloop()

    # Error if user forgets to select workout type
    elif VAR.get() == 0:
        popup = tk.Tk()
        popup.title('Error')
        popup.geometry('200x100')
        error_label = tk.Label(popup, text='ERROR:\nMust select a type of workout.')
        error_label.pack(padx=10, pady=5)
        close_button = tk.Button(popup, text='Close', command=popup.destroy)
        close_button.pack(padx=10, pady=5)
        popup.mainloop()

    else:
        # Create loading bar for rendering process
        popup = tk.Tk()
        popup.title("Rendering in Progress")
        popup.geometry('400x200')
        label = tk.Label(popup, text='Please wait as the video renders.\nThis could take a couple of minutes.')
        label.pack(padx=10, pady=5)
        renderingProgress = ttk.Progressbar(popup, orient='horizontal',
                                            length=200, mode='determinate')
        renderingProgress.pack(padx=10, pady=5)
        renderingProgress['value'] += 20
        popup.update()
        renderingProgress['value'] += 30
        popup.update()

    # Squat Processing
    if VAR.get() == 1:
        squat = pvt.SquatExercise()
        vid_name = entryBox.get() + '.avi'
        pvt.process_video_op(VIDEO, vid_name, VAR.get())
        dir_name = entryBox.get() + '_files'
        renderingProgress['value'] += 20
        popup.update()
        renderingProgress['value'] += 20
        popup.update()
        os.system('mkdir ' + dir_name)
        os.system('move ' + vid_name + ' ' + dir_name)
        os.system('move rep_graph.png ' + dir_name)
        os.chdir(dir_name)
        end = time.time()
        print(end - start, "seconds")
        os.system(vid_name)
        popup.destroy()


root = tk.Tk()
root.title("Exercise Evaluation Program")
root.configure(bg='grey')

topPicFrame = tk.Frame(root, bg='grey')
topPicFrame.grid(column=2, row=0)

topImg = ImageTk.PhotoImage(Image.open('before.jpg').resize((300, 200)), Image.ANTIALIAS)
topCan = tk.Canvas(topPicFrame, bg='grey', height=210, width=310)
topCan.background = topImg
bg1 = topCan.create_image((157, 107), image=topImg)
topCan.grid(column=0, row=1)

topLabel = tk.Label(topPicFrame, text='Before', fg='white', bg='maroon',
                    padx=10, pady=5)
topLabel.grid(column=0, row=0)


bottomPicFrame = tk.Frame(root, bg='grey')
bottomPicFrame.grid(column=2, row=1, rowspan=2)

bottomImg = ImageTk.PhotoImage(Image.open('frame0334.jpg').resize((300, 200)), Image.ANTIALIAS)
bottomCan = tk.Canvas(bottomPicFrame, bg='grey', height=210, width=310)
bottomCan.background = bottomImg
bg2 = bottomCan.create_image(157, 107, image=bottomImg)
bottomCan.grid(column=0, row=1)

bottomLabel = tk.Label(bottomPicFrame, text='After', fg='white', bg='maroon',
                       padx=10, pady=5)
bottomLabel.grid(column=0, row=0)

# Creating radio button frame
radioFrame = tk.Frame(root, bg='grey')
radioFrame.grid(column=0, row=0)

VAR = tk.IntVar()

# Creating radio buttons
exercise1 = tk.Radiobutton(radioFrame, text="Squat", variable=VAR, value=1, width=10,
                           padx=10, pady=5, bg="grey")
exercise2 = tk.Radiobutton(radioFrame, text="Lunge", variable=VAR, value=2, width=10,
                           padx=10, pady=5, bg="grey")
exercise3 = tk.Radiobutton(radioFrame, text="Bicep Curl", variable=VAR, value=3, width=10,
                           padx=10, pady=5, bg="grey")
exercise4 = tk.Radiobutton(radioFrame, text="Shoulder Press", variable=VAR, value=4, width=10,
                           padx=10, pady=5, bg="grey")

# Placing radio buttons
exercise1.grid(column=0, row=0)
exercise2.grid(column=0, row=1)
exercise3.grid(column=0, row=2)
exercise4.grid(column=0, row=3)

# Creating frame for buttons
buttonFrame = tk.Frame(root, bg='grey')
buttonFrame.grid(column=1, row=0)

# Creating buttons
select_video = tk.Button(buttonFrame, text="Select Video", bg="maroon",
                         fg="white", padx=10, pady=5,
                         width=10, command=get_video)
process_video = tk.Button(buttonFrame, text="Process Video", bg="maroon",
                          fg="white", padx=10, pady=5,
                          width=10, command=process_video)

STR_VAR = tk.StringVar()

# Placing buttons
select_video.grid(column=0, row=0, rowspan=2)
process_video.grid(column=0, row=2, rowspan=2)

# Creating selected video label
video_label = tk.Label(root, text="Video Selected: " + VIDEO, bg="grey",
                       padx=5, pady=5, fg="white", width=50)
# Placing label
video_label.grid(column=0, row=1, columnspan=2)

# Creating frame for entry and label
entryFrame = tk.Frame(root, bg='grey')
entryFrame.grid(column=0, row=2, columnspan=2)

# Creating label with instructions
infoLabel = tk.Label(entryFrame, bg='grey', fg='white',
                     text="Type the name you would like"
                     " to save the processed video as.\n"
                     "Each rep will be graphed on a plot.\n"
                     "Both the processed video and the graph will\n"
                     "be saved in a directory titled givenName_files")
# Placing label
infoLabel.grid(column=0, row=0)
# Creating entry widget
entryBox = tk.Entry(entryFrame, width=40, textvariable=STR_VAR,
                    text="Type name of the processed video")
# Placing entry
entryBox.grid(column=0, row=1)

tk.mainloop()
