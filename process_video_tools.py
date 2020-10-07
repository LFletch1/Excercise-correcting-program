#!/usr/bin/env python3
# Lance Fletcher
# July 6, 2020

import rep_graphing_tool as rep_graph
import sys
import cv2
import os
from sys import platform
import argparse
import time
import matplotlib.pyplot as plt
import scipy.signal
from math import sqrt, acos, pi


def calculate_angle(point1X, point1Y, angle_pointX, angle_pointY, point2X, point2Y):
    # prevents division by zero
    if point1X == 0 or point1Y == 0 or angle_pointX == 0 or angle_pointY == 0 or point2X == 0 or point2Y == 0:
        return 0
    # use formula arccos((vectorA * vectorB)/(normalizedVectorA * normalizedVectorB)) where * = dot product
    vectorDotProduct = (((point1X - angle_pointX) * (point2X - angle_pointX)) + (
            (point1Y - angle_pointY) * (point2Y - angle_pointY)))
    normalizedVectorDotProduct = (sqrt((pow((point1X - angle_pointX), 2)) + pow((point1Y - angle_pointY), 2)) * sqrt(
        pow((point2X - angle_pointX), 2)) + (pow((point2Y - angle_pointY), 2)))
    quotient = (vectorDotProduct / normalizedVectorDotProduct)
    if quotient > 1:
        quotient = 1
    elif quotient < -1:
        quotient = -1
    angle = acos(quotient)
    # convert from radians to degrees
    angle *= (180 / pi)
    return round(angle, 2)


class Plot:
    def __init__(self, values):
        self.values = values
        self.curves = []
        self.low = 2000  # start with high value to make first number the low
        self.high = -2000  # start with low value to make the first number the high
        self.start = 0
        self.end = 0
        self.high_index = 0
        self.low_index = 0
        self.rising = False
        self.falling = True


class SquatExercise:
    def __init__(self):
        self.reps = 0
        self.peak = False
        self.total_frames = 0
        self.total_grade = 0
        self.g1Total = 0  # grade 1 total / total_frames = g1Avg
        self.g2Total = 0
        self.g3Total = 0
        self.g4Total = 0
        self.angles = []
        self.grades = []

        # methods
        # add_frame_to_exercise(person)
        # create_exercise_summary
        # average time of each rep
        # average score of entire exercise
        # varience in score
        # Things to work on: Based on grade averages

    def analyze_squat_frame(self, person):
        """Weighted average grading scale of a squat\n
            person: instance of person BodyConstruct class\n
            current_rep: current rep to be passed through by user\n
            peak: boolean describing whether the exercise has hit its peak"""
        knee_angle = calculate_angle(person.r_hip.x, person.r_hip.y,
                                     person.r_knee.x, person.r_knee.y,
                                     person.r_ankle.x, person.r_ankle.y)
        hip_angle = calculate_angle(person.r_knee.x, person.r_knee.y,
                                    person.r_hip.x, person.r_hip.y,
                                    person.neck.x, person.neck.y)
        head_angle = calculate_angle(person.mid_hip.x, person.mid_hip.y,
                                     person.neck.x, person.neck.y,
                                     person.nose.x, person.nose.y)

        # logic to determine if start of new rep
        if knee_angle <= 100 and not self.peak:
            self.peak = True
            self.reps += 1
        if knee_angle > 120 and self.peak:
            self.peak = False

        # Horizontal Movement of Bar
        grade1 = 100
        center_distance = abs(person.neck.x - person.r_ankle.x)
        if center_distance > 40:
            # Chest is too extended over feet
            grade1 -= center_distance - 40
        self.g1Total += grade1

        # Knee Angle vs. Hip Angle Comparison
        grade2 = 100
        angle_difference = abs(knee_angle - hip_angle)
        if angle_difference > 3:
            grade2 -= 2 * angle_difference
        self.g2Total += grade2

        # Head alignment comparison
        grade3 = 100
        if head_angle < 125:
            grade3 -= abs(125 - head_angle)
        self.g3Total += grade3

        # Shoulders in correct placement.
        grade4 = 100
        shoulder_distance = abs(person.r_shoulder.x - person.neck.x)
        if shoulder_distance > 30:
            grade4 -= shoulder_distance - 30
        self.g4Total += grade4

        # Weighted Average
        frame_grade = round((.3 * grade1) + (.4 * grade2) + (.2 * grade3) + (.1 * grade4))
        self.total_frames += 1
        self.total_grade += frame_grade
        self.angles.append(knee_angle)
        self.grades.append(frame_grade)
        return frame_grade, knee_angle

    def produce_summary_and_graph(self):
        # smooth plot
        sg_angles = scipy.signal.savgol_filter(self.angles, 55, 3)
        sg_plot = Plot(sg_angles)
        index = 0
        consecutive_changes = 0
        lows = []
        low_indexes = []
        highs = []
        high_indexes = []
        while index < len(sg_plot.values):
            if sg_plot.falling:  # values are going down in value
                if consecutive_changes == 10:  # Curve has been rising for 10 indexes, we know its turned upward
                    sg_plot.falling = False
                    sg_plot.rising = True
                    lows.append(sg_plot.low)
                    low_indexes.append(sg_plot.low_index)
                    sg_plot.low = 2000  # Reset low to high value for next time through loop
                    consecutive_changes = 0
                elif sg_plot.values[index] < sg_plot.low:
                    sg_plot.low = sg_plot.values[index]
                    sg_plot.low_index = index
                    consecutive_changes = 0
                else:
                    consecutive_changes += 1
            else:  # values are going up in value
                if consecutive_changes == 10:  # Curve has been falling for 10 indexes, we know its turned downward
                    # print('high:', sg_plot.high_index)
                    sg_plot.rising = False
                    sg_plot.falling = True
                    highs.append(sg_plot.high)
                    high_indexes.append(sg_plot.high_index)
                    sg_plot.high = -2000  # Reset high to low value for next time through loop
                    consecutive_changes = 0
                elif sg_plot.values[index] > sg_plot.high:
                    sg_plot.high = sg_plot.values[index]
                    sg_plot.high_index = index
                    consecutive_changes = 0
                else:
                    consecutive_changes += 1
            index += 1

        # set up plot and the background
        fig = plt.figure()
        ax = plt.axes()
        ax.set_facecolor('grey')
        fig.patch.set_facecolor('grey')
        line_styles = ('solid', 'dashed', 'dotted', 'dashdot')
        rep = 0
        i = 0
        total = 0
        total_rep_frames = 0  # total amount of frames that happen during the exercise
        # break up entire plot into curves that represent each rep
        # The beginning of a rep is a high point and the end of the rep is a high point
        # Thus we know the range of a rep is from one high point to another
        while i < len(high_indexes) - 1:
            total = 0  # set toat
            LINE_STYLE = rep % 4  # cycles through line_style tuple
            rep_angles = sg_angles[high_indexes[i]:high_indexes[i + 1]]
            rep_grades = self.grades[high_indexes[i]:high_indexes[i + 1]]
            i += 1
            if len(rep_angles) < 50:  # rep wasn't long enough meaning it probably was not actually a rep
                continue
            rep += 1  # add one to rep
            for num in rep_grades:
                total += num
            average_grade = total / len(rep_grades)
            total_rep_frames += len(rep_grades)
            if average_grade > 85:
                COLOR = 'green'
            elif average_grade > 70:
                COLOR = 'yellow'
            elif average_grade > 55:
                COLOR = 'orange'
            else:
                COLOR = 'red'
            plt.plot(rep_angles, color=COLOR, label='Rep ' + str(rep), linestyle=line_styles[LINE_STYLE])
            plt.legend()

        plt.savefig('rep_graph')

        # create exercise summary report
        text_file = open('Exercise Summary', 'w+')
        text_file.write("Exercise Summary\n")
        average_frame_grade = self.total_grade / self.total_frames
        text_file.write("Average grade of exercise: " + str(average_frame_grade) + "\n")
        time_of_reps_seconds = total_rep_frames / 30  # 30 = frame rate
        average_rep_time = time_of_reps_seconds / self.reps
        text_file.write("Tempo: " + str(average_rep_time) + "\n")
        exercise_corrections = ""
        if (self.g1Total / self.reps) < 80:
            exercise_corrections += "Move bar vertical"
        if (self.g2Total / self.reps) < 80:
            exercise_corrections += "Hip vs Knee"
        if (self.g3Total / self.reps) < 80:
            exercise_corrections += "Head Alignment"
        if (self.g4Total / self.reps) < 80:
            exercise_corrections += "Shoulder"
        text_file.write("Exercise Recommendations" + exercise_corrections + "\n")


class BodyPoint:
    def __init__(self, x_point, y_point):
        self.x = x_point
        self.y = y_point


class BodyConstruct:
    def __init__(self, BodyPoint_array):
        self.nose = BodyPoint_array[0]
        self.neck = BodyPoint_array[1]
        self.r_shoulder = BodyPoint_array[2]
        self.r_elbow = BodyPoint_array[3]
        self.r_wrist = BodyPoint_array[4]
        self.l_shoulder = BodyPoint_array[5]
        self.l_elbow = BodyPoint_array[6]
        self.l_wrist = BodyPoint_array[7]
        self.mid_hip = BodyPoint_array[8]
        self.r_hip = BodyPoint_array[9]
        self.r_knee = BodyPoint_array[10]
        self.r_ankle = BodyPoint_array[11]
        self.l_hip = BodyPoint_array[12]
        self.l_knee = BodyPoint_array[13]
        self.l_ankle = BodyPoint_array[14]
        self.r_eye = BodyPoint_array[15]
        self.l_eye = BodyPoint_array[16]
        self.r_ear = BodyPoint_array[17]
        self.l_ear = BodyPoint_array[18]
        self.l_big_toe = BodyPoint_array[19]
        self.l_small_toe = BodyPoint_array[20]
        self.l_heel = BodyPoint_array[21]
        self.r_big_toe = BodyPoint_array[22]
        self.r_small_toe = BodyPoint_array[23]
        self.r_heel = BodyPoint_array[24]


def split_video_into_frames(video_file):
    currentFrame = 0
    # Playing video from file:
    cap = cv2.VideoCapture(video_file)
    # print(video_file)
    try:
        if not os.path.exists('frames'):
            os.makedirs('frames')
    except OSError:
        print('Error: Creating directory of frame .jpg')
    ret = True
    while ret:
        ret, frame = cap.read()
        if not ret:
            continue
        # print(ret)
        name = './frames/frame' + str(currentFrame).zfill(4) + '.jpg'
        # print(name)
        # print('Creating...' + name)
        cv2.imwrite(name, frame)
        currentFrame += 1


def create_body_construct(data_array):
    BodyPoints_array = []
    nose = BodyPoint(data_array[0][0][0], data_array[0][0][1])
    BodyPoints_array.append(nose)
    neck = BodyPoint(data_array[0][1][0], data_array[0][1][1])
    BodyPoints_array.append(neck)
    r_shoulder = BodyPoint(data_array[0][2][0], data_array[0][2][1])
    BodyPoints_array.append(r_shoulder)
    r_elbow = BodyPoint(data_array[0][3][0], data_array[0][3][1])
    BodyPoints_array.append(r_elbow)
    r_wrist = BodyPoint(data_array[0][4][0], data_array[0][4][1])
    BodyPoints_array.append(r_wrist)
    l_shoulder = BodyPoint(data_array[0][5][0], data_array[0][5][1])
    BodyPoints_array.append(l_shoulder)
    l_elbow = BodyPoint(data_array[0][6][0], data_array[0][6][1])
    BodyPoints_array.append(l_elbow)
    l_wrist = BodyPoint(data_array[0][7][0], data_array[0][7][1])
    BodyPoints_array.append(l_wrist)
    mid_hip = BodyPoint(data_array[0][8][0], data_array[0][8][1])
    BodyPoints_array.append(mid_hip)
    r_hip = BodyPoint(data_array[0][9][0], data_array[0][9][1])
    BodyPoints_array.append(r_hip)
    r_knee = BodyPoint(data_array[0][10][0], data_array[0][10][1])
    BodyPoints_array.append(r_knee)
    r_ankle = BodyPoint(data_array[0][11][0], data_array[0][11][1])
    BodyPoints_array.append(r_ankle)
    l_hip = BodyPoint(data_array[0][12][0], data_array[0][12][1])
    BodyPoints_array.append(l_hip)
    l_knee = BodyPoint(data_array[0][13][0], data_array[0][13][1])
    BodyPoints_array.append(l_knee)
    l_ankle = BodyPoint(data_array[0][14][0], data_array[0][14][1])
    BodyPoints_array.append(l_ankle)
    r_eye = BodyPoint(data_array[0][15][0], data_array[0][15][1])
    BodyPoints_array.append(r_eye)
    l_eye = BodyPoint(data_array[0][16][0], data_array[0][16][1])
    BodyPoints_array.append(l_eye)
    r_ear = BodyPoint(data_array[0][17][0], data_array[0][17][1])
    BodyPoints_array.append(r_ear)
    l_ear = BodyPoint(data_array[0][18][0], data_array[0][18][1])
    BodyPoints_array.append(l_ear)
    l_big_toe = BodyPoint(data_array[0][19][0], data_array[0][19][1])
    BodyPoints_array.append(l_big_toe)
    l_small_toe = BodyPoint(data_array[0][20][0], data_array[0][20][1])
    BodyPoints_array.append(l_small_toe)
    l_heel = BodyPoint(data_array[0][21][0], data_array[0][21][1])
    BodyPoints_array.append(l_heel)
    r_big_toe = BodyPoint(data_array[0][22][0], data_array[0][22][1])
    BodyPoints_array.append(r_big_toe)
    r_small_toe = BodyPoint(data_array[0][23][0], data_array[0][23][1])
    BodyPoints_array.append(r_small_toe)
    r_heel = BodyPoint(data_array[0][24][0], data_array[0][24][1])
    BodyPoints_array.append(r_heel)
    current_body_construct = BodyConstruct(BodyPoints_array)
    return current_body_construct


def delete_directory(directory):
    dir = str(directory)
    for file in os.listdir('frames'):
        os.remove('frames/' + file)
    os.rmdir('frames')


def process_video_op(video,video_name, option):
    # Utilize openpose python API to directly process images and get output
    # Changed dir_path to point to correct directory
    # START OF OPENPOSE CODE
    try:
        # Import Openpose (Windows/Ubuntu/OSX)
        dir_path = "C:\\Users\\lance\\Documents\\openpose-master\\openpose-master\\build\\examples\\tutorial_api_python"
        try:
            # Windows Import
            if platform == "win32":
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append(dir_path + '/../../python/openpose/Release');
                os.environ['PATH'] = os.environ[
                                         'PATH'] + ';' + dir_path + '/../../x64/Release;' + dir_path + '/../../bin;'
                import pyopenpose as op
            else:
                # Change these variables to point to the correct folder (Release/x64 etc.)
                sys.path.append('C:\\Users\\lance\\Documents\\openpose-master\\openpose-master\\build\\python');
                # sys.path.append('../../python');
                # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
                # sys.path.append('/usr/local/python')
                from openpose import pyopenpose as op
        except ImportError as e:
            print(
                'Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
            raise e

        # Flags
        parser = argparse.ArgumentParser()
        parser.add_argument("--image_dir", default="frames",
                            help="Process a directory of images. Read all standard formats (jpg, png, bmp, etc.).")
        parser.add_argument("--no_display", default=True, help="Enable to disable the visual display.")
        args = parser.parse_known_args()

        # Custom Params (refer to include/openpose/flags.hpp for more parameters)
        params = dict()
        params["model_folder"] = "C:\\Users\\lance\\Documents\\openpose-master\\openpose-master\\models"
        params["number_people_max"] = 1

        # Add others in path?
        for i in range(0, len(args[1])):
            curr_item = args[1][i]
            if i != len(args[1]) - 1:
                next_item = args[1][i + 1]
            else:
                next_item = "1"
            if "--" in curr_item and "--" in next_item:
                key = curr_item.replace('-', '')
                if key not in params:  params[key] = "1"
            elif "--" in curr_item and "--" not in next_item:
                key = curr_item.replace('-', '')
                if key not in params: params[key] = next_item

        # Starting OpenPose
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()

        # Split given video into frames
        vid_filepath = video
        split_video_into_frames(vid_filepath)

        # Read frames on directory
        imagePaths = op.get_images_on_directory(args[0].image_dir)
        start = time.time()
        # END OF OPENPOSE CODE

        # Compile all the frames into a video
        size = (1920, 1080)
        out = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'XVID'), 30, size)  # MJPG
        # peak = False
        # reps = 0
        # angles = []
        # grades = []
        if option == 1:
            exercise = SquatExercise()
            # analysis_function = exercise.analyze_squat_frame
        for imagePath in imagePaths:
            # Process and display images
            datum = op.Datum()
            imageToProcess = cv2.imread(imagePath)
            datum.cvInputData = imageToProcess
            opWrapper.emplaceAndPop([datum])

            # Openpose has extracted data from the frame
            frame = datum.cvOutputData
            pose = create_body_construct(datum.poseKeypoints) # datum.PoseKeypoints holds body point values
            grade, angle = exercise.analyze_squat_frame(pose)
            # grades.append(grade)
            # angles.append(angle)
            # change color based on grade of workout
            if grade > 85:
                color = (31, 150, 27)  # green
            elif grade > 70:
                color = (0, 255, 255)  # yellow
            elif grade > 55:
                color = (25, 179, 255)  # orange
            else:
                color = (0, 0, 255)  # red
            cv2.putText(frame, (str(angle)),
                        (round(pose.r_knee.x), round(pose.r_knee.y)), cv2.FONT_HERSHEY_SIMPLEX,
                        2, (255, 255, 255, 255), 2)
            cv2.putText(frame, ("Reps: " + str(exercise.reps)),
                        (round(pose.nose.x), round(pose.nose.y)), cv2.FONT_HERSHEY_SIMPLEX,
                        3, (255, 255, 255, 255), 3)
            cv2.putText(frame, str(grade),
                        (10, 1020), cv2.FONT_HERSHEY_SIMPLEX,
                        3, color, 3)
            out.write(frame)
            os.remove(imagePath)
            if not args[0].no_display:
                cv2.imshow("OpenPose 1.6.0 - Tutorial Python API", datum.cvOutputData)
                key = cv2.waitKey(15)
                if key == 27:
                    break
        out.release()
        # rep_graph.graph_graded_smooth_plot(angles, grades)
        exercise.produce_summary_and_graph()
        end = time.time()
        print("OpenPose demo successfully finished. Total time: " + str(end - start) + " seconds")
        # for file in os.listdir('frames'):
        #     os.remove('frames/' + file)
        os.rmdir('frames')
    except IndexError as c:
        print(c)
        exercise.produce_summary_and_graph()
    except Exception as e:
        print(e)
        sys.exit(-1)