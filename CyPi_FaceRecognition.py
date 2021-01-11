import os, cv2, face_recognition, datetime
import numpy as np
from PIL import Image
from datetime import datetime 
# import time instead of datetime and adjust functions to be more international timezone(s) compatible
from FaceRec import routing_cases_2

# CyPi - Team 4 - Leon Zhu
# Main facial recognition program
# Uses face-recognition, OpenCV (cv2), and Image (from pillow) libraries
# Some code from face-recognition examples [ Github: https://github.com/ageitgey/face_recognition ]

DIRNAME = os.path.dirname(__file__)  # get root project directory and store
print(DIRNAME)

# Load authorized users for facial recognition
def loadAuthUsers():
    
    #/home/pi/FaceRec
    knownNames = os.path.join(DIRNAME, 'KnownFaces', 'KnownNames.txt')
    knownFaces = os.path.join(DIRNAME, 'KnownFaces')

    # Load known names
    with open(knownNames, 'r') as namesFile:
        names = namesFile.readlines()
        for each in names:
            known_face_names.append(each.strip())

    # Create and load known face encodings
    for each in known_face_names:  

        imageFile = r'%s\%s.jpg' % (knownFaces, each)
        new_image = face_recognition.load_image_file(imageFile)
        new_face_encoding = face_recognition.face_encodings(new_image)[0]
        known_face_encodings.append(new_face_encoding)

    return known_face_encodings, known_face_names


def updateAuthUsers(): ##cant get this function to work right
    # /home/pi/FaceRec
    knownNames = os.path.join(DIRNAME, 'KnownFaces', 'KnownNames.txt')
    knownFaces = os.path.join(DIRNAME, 'KnownFaces')

    # Load known names and remove ones already loaded
    print('updating database...')
    with open(knownNames, 'r') as namesFile:
        names = namesFile.readlines()
        names2 = []
        for name in names:
            names2.append(name.strip())    # correcting trailing whitespace
        names = names2
        for each in reversed(names):
            if each in known_face_names:
                known_face_names.append(each.strip())
                print('added ' + each)
                names.remove(each)



    # Create and load known face encodings
    for each in names:
        imageFile = r'%s\%s.jpg' % (knownFaces, each)
        new_image = face_recognition.load_image_file(imageFile)
        new_face_encoding = face_recognition.face_encodings(new_image)[0]
        known_face_encodings.append(new_face_encoding)
        print('added encoding for '  + each)

    print("finished.")


# Log data
def logData(eventNum, camImage):

    # Get current date and time in strings
    currDateTime = datetime.now()
    currDate = currDateTime.date().strftime('%m%d%Y')
    currTime = currDateTime.time().strftime('%H%M%S')
    imageStr = '%s.jpg' % currTime
    logStr = currDateTime.strftime('%m/%d/%Y_%H:%M:%S')

    "./"
    # Directory and text file name based on current date
    #eventsDir = '' % currDate
    eventsDir = os.path.join(DIRNAME, currDate)
    #eventsTxt = r'%s\%s_Events.txt' % (eventsDir, currDate)
    eventsTxt = os.path.join(eventsDir, currDate)

    # If directory doesnt exist, make it and accompanying text file
    if not os.path.exists(eventsDir):
        os.mkdir(eventsDir)
        newTxt = open(eventsTxt, 'w')
        newTxt.close()

    # Save image from camera feed
    os.chdir(eventsDir)
    cv2.imwrite(imageStr, camImage)

    if eventNum == 1:
        eventStr = 'Unknown Face Detected'
    else:
        eventStr = 'Other Event'

    # Add new log line string
    eventStr = '%s - %s (%s)' % (logStr, eventStr, imageStr)
    with open(eventsTxt, 'a') as aLog:
        aLog.write(eventStr + '\n')

def main():
    global known_face_names
    global known_face_encodings
    # Load in video stream from DEFAULT webcam
    # ADDED: Option to load video from remote path instead
    remote_video_path = 'http://192.168.50.54:8081/'
    #video_capture = cv2.VideoCapture(remote_video_path)
    video_capture = cv2.VideoCapture(0)
    cv2.namedWindow('Video')

    # Initilize variables and load known faces
    face_locations, face_encodings = [], []
    known_face_encodings, known_face_names = loadAuthUsers()

    # Process every 8th frame
    process_this_frame = 8

    #ADDED: To enable grace period before unknown face event is logged
    unknown_face_frames = 0

    #ADDED To update the image database every specified number of analyzed frames.
    update_database = 0

    face_names = []    # ADDED:added a declaration here to prevent reference before assignment
    while True:
        update_database += 1
        if update_database >= 10000:
            face_locations, face_encodings = [], []
            known_face_encodings = []
            known_face_encodings, known_face_names = loadAuthUsers()
            print('Database updated.')
            update_database = 0
        # Grab a single frame of video, resize to 1/4 scale for faster processing, and convert colors 
        ret, frame = video_capture.read()
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]

        processed = False

        # Only process every other frame
        if process_this_frame == 8:
            # loadAuthUsers()
            process_this_frame = 0
            processed = True

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


            face_names = []
            for face_encoding in face_encodings:

                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)


                # Event
                if matches[best_match_index]:
                    print(matches)
                    name = known_face_names[best_match_index]
                    print('Known face %s has been detected' % name)
                else:
                    name = 'Unknown'
                    #print('Unknown face has been detected')
                face_names.append(name)


            if 'Unknown' in face_names:
                unknown_face_frames += 1
                print(f'Unknown face detected for {unknown_face_frames} consecutive frames')

            if unknown_face_frames >= 3:
                print('unknown face grace period exceeded, logging event.')
                logData(1, frame)
                unknown_face_frames = 0


        process_this_frame += 1

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

        # Display the resulting image, comment this out to only run in a terminal
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    known_face_encodings = []
    known_face_names = []
    main()

