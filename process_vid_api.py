#!/usr/bin/env python3
# Lance Fletcher
# August 21, 2020

import sys
import cv2
import os
from sys import platform
import argparse
import time
import process_video_tools as pvt


def process_video_op(video):
    try:
        # Import Openpose (Windows/Ubuntu/OSX)
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        dir_path = "C:\\Users\\lance\\Documents\\openpose-master\\openpose-master\\build\\examples\\tutorial_api_python"
        try:
            # Windows Import
            if platform == "win32":
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append(dir_path + '/../../python/openpose/Release');
                os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
                import pyopenpose as op
            else:
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append('C:\\Users\\lance\\Documents\\openpose-master\\openpose-master\\build\\python');
                # sys.path.append('../../python');
                # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
                # sys.path.append('/usr/local/python')
                from openpose import pyopenpose as op
        except ImportError as e:
            print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
            raise e

        # Flags
        parser = argparse.ArgumentParser()
        parser.add_argument("--image_dir", default="frames", help="Process a directory of images. Read all standard formats (jpg, png, bmp, etc.).")
        parser.add_argument("--no_display", default=True, help="Enable to disable the visual display.")
        args = parser.parse_known_args()

        # Custom Params (refer to include/openpose/flags.hpp for more parameters)
        params = dict()
        params["model_folder"] = "C:\\Users\\lance\\Documents\\openpose-master\\openpose-master\\models"
        params["number_people_max"] = 1

        # Add others in path?
        for i in range(0, len(args[1])):
            curr_item = args[1][i]
            if i != len(args[1])-1: next_item = args[1][i+1]
            else: next_item = "1"
            if "--" in curr_item and "--" in next_item:
                key = curr_item.replace('-', '')
                if key not in params:  params[key] = "1"
            elif "--" in curr_item and "--" not in next_item:
                key = curr_item.replace('-', '')
                if key not in params: params[key] = next_item

        # Construct it from system arguments
        # op.init_argv(args[1])
        # oppython = op.OpenposePython()

        # Starting OpenPose
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()
        # Split given video into frames
        vid_filepath = video
        pvt.split_video_into_frames(vid_filepath)

        # Read frames on directory
        imagePaths = op.get_images_on_directory(args[0].image_dir)
        start = time.time()
        # Process and display images
        loop_num = 0
        size = (1920, 1080)
        out = cv2.VideoWriter('new_video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, size)  # MJPG
        for imagePath in imagePaths:
            datum = op.Datum()
            imageToProcess = cv2.imread(imagePath)
            datum.cvInputData = imageToProcess
            opWrapper.emplaceAndPop([datum])

            person = pvt.create_body_construct(datum.poseKeypoints)

            print("Body keypoints: \n" + str(datum.poseKeypoints))
            print(person.r_knee.x)
            img = datum.cvOutputData
            out.write(img)
            if not args[0].no_display:
                cv2.imshow("OpenPose 1.6.0 - Tutorial Python API", datum.cvOutputData)
                key = cv2.waitKey(15)
                if key == 27:
                    break
        out.release()

        end = time.time()
        print("OpenPose demo successfully finished. Total time: " + str(end - start) + " seconds")
    except Exception as e:
        print(e)
        sys.exit(-1)
