import argparse
import os

import cv2


def drag_and_crop(event, x, y, flags, param):
    global refPt, cropping
    if event == cv2.EVENT_LBUTTONDOWN:
        refPt.append((x, y))
        cropping = True

    elif event == cv2.EVENT_LBUTTONUP:
        refPt.append((x, y))
        cropping = False


def parse_roi():
    # Allows you to make the ROI in any direction, not just top left to bottom right
    global refPt
    xlist = [refPt[0][0], refPt[1][0]]
    ylist = [refPt[0][1], refPt[1][1]]
    if xlist[0] == xlist[1]:
        refPt = []
        return
    refPt = []
    refPt.append((min(xlist), min(ylist)))
    refPt.append((max(xlist), max(ylist)))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--video", type=str, required=True,
                        help="File path to the Video")
    parser.add_argument("-o", "--output", type=str, required=False,
                        help="File path to the output folder. If no file given it will create a folder called Output.")
    args = parser.parse_args()
    if not args.output:
        output_path = os.getcwd() + '/Data/Output/'
        if not os.path.isdir(output_path):
            try:
                os.makedirs(output_path)
                print('Created output folder with path: {}'.format(output_path))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        args.output = output_path
    output_path = args.output
    video_path = args.video
    return video_path, output_path


def crop_roi(filepath, output_path):
    global refPt, cropping
    cap = cv2.VideoCapture(os.getcwd() + filepath)
    if (cap.isOpened() == False):
        print("Error opening video stream or file")
    refPt = []
    cropping = False
    frame_count = 1
    print('Press q at anytime to quit')
    while(cap.isOpened()):
        ret, frame = cap.read()
        clone = frame.copy()
        if ret == True:
            frame_count += 1
            cv2.imshow('Frame', frame)
            cv2.namedWindow('Frame')
            cv2.setMouseCallback('Frame', drag_and_crop)
            cv2.waitKey(1)
            face_count = 1
            while True:
                key = cv2.waitKey(1) & 0xFF
                if len(refPt) == 2:
                    parse_roi()
                    if len(refPt) == 0:
                        # Doesn't count single mice clicks as crop regions
                        continue
                    cv2.rectangle(frame, refPt[0], refPt[1], (0, 255, 0), 2)
                    cv2.imshow("Frame", frame)
                    roi = clone[refPt[0][1]:refPt[1]
                                [1], refPt[0][0]:refPt[1][0]]
                    cv2.imwrite((output_path + "frame%d-%d.jpg" %
                                 (frame_count, face_count)), roi)
                    refPt = []
                    face_count += 1
                if key == ord('e'):
                    break
                if key == ord('q'):
                    cap.release()
                    cv2.destroyAllWindows()
                    return
                if key == ord('r'):
                    for img_num in range(face_count, 0, -1):
                        if os.path.exists((output_path + "frame%d-%d.jpg" % (frame_count, img_num))):
                            os.remove((output_path + "frame%d-%d.jpg" %
                                       (frame_count, img_num)))
                    frame = clone.copy()
                    cv2.imshow('Frame', frame)
                    face_count = 1
            continue
        else:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    input_path, output_path = parse_args()
    crop_roi(input_path, output_path)
