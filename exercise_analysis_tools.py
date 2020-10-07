#!/usr/bin/env python3
# Lance Fletcher
# July 6, 2020

from math import sqrt, acos, pi


def calculate_angle(point1X, point1Y, angle_pointX, angle_pointY, point2X, point2Y):
    # prevents division by zero
    if point1X == 0 or point1Y == 0 or angle_pointX == 0 or angle_pointY == 0 or point2X == 0 or point2Y == 0:
        return 0
    # use formuala arccos((vectorA * vectorB)/(normalizedVectorA * normalizedVectorB)) where * = dot product
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


# person - an instance of the body construct class which contains 25 key body points
# current rep - current repetition of the exercises being performed
# peak - used to dictate amount of reps
def analyze_squat(person, current_rep, peak):
    # Check if head is up
    head_angle = calculate_angle(person.mid_hip.x, person.mid_hip.y,
                                 person.neck.x, person.neck.y,
                                 person.nose.x, person.nose.y)
    message = ""
    # print(head_angle)
    if head_angle <= 125:
        message += "Head is down"

    if (person.r_ankle.x + 60) < person.neck.x or (person.r_ankle.x - 60) > person.neck.x:
        message += " Adjust center of gravity."

    knee_angle = calculate_angle(person.r_hip.x, person.r_hip.y, person.r_knee.x, person.r_knee.y, person.r_ankle.x,
                                 person.r_ankle.y)
    if knee_angle <= 100 and not peak:
        peak = True
        current_rep += 1
    if knee_angle > 120 and peak:
        peak = False

    if message == "":
        message = "GOOD FORM"

    return message, current_rep, peak, knee_angle


def new_analyze_squat(person, current_rep, peak):
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

    if knee_angle <= 100 and not peak:
        peak = True
        current_rep += 1
    if knee_angle > 120 and peak:
        peak = False

    # Horizontal Movement of Bar
    grade1 = 100
    center_distance = abs(person.neck.x - person.r_ankle.x)
    if center_distance > 40:
        # Chest is too extended over feet
        grade1 -= center_distance - 40

    # Knee Angle vs. Hip Angle Comparison
    grade2 = 100
    angle_difference = abs(knee_angle - hip_angle)
    if angle_difference > 3:
        grade2 -= 2 * angle_difference

    # Head alignment comparison
    grade3 = 100
    if head_angle < 125:
        grade3 -= abs(125 - head_angle)

    # Shoulders in correct placement.
    grade4 = 100
    shoulder_distance = abs(person.r_shoulder.x - person.neck.x)
    if shoulder_distance > 30:
        grade4 -= shoulder_distance - 30

    # Weighted Average
    frame_grade = round((.3 * grade1) + (.4 * grade2) + (.2 * grade3) + (.1 * grade4))
    
    return frame_grade, current_rep, peak, knee_angle
