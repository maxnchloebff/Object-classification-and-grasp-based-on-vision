import cv2
import numpy as np
import matplotlib.pyplot as plt

mouse_pos = np.array([-1, -1])


def on_mouse(event, x, y, flags, param):
    global mouse_pos
    if event == cv2.EVENT_FLAG_LBUTTON:
        mouse_pos = np.array([x, y])


capture = cv2.VideoCapture(0)
cv2.namedWindow('camera', cv2.WINDOW_AUTOSIZE)
cv2.setMouseCallback('camera', on_mouse)

while True:
    ret, frame = capture.read()
    cv2.putText(frame, str(mouse_pos), (20, 20), cv2.FONT_HERSHEY_PLAIN, 0.75, (0, 255, 0))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cv2.imshow('camera', gray)

    if cv2.waitKey(1) == ord('q'):
        gray_bk = gray
        plt.imshow(gray)
        plt.show()
        break

capture.release()
cv2.destroyAllWindows()
