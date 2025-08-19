import cv2

IMG_W = 1280
IMG_H = 720

video:cv2.VideoCapture

def openCam():
    global video
    video = cv2.VideoCapture(1)
    video.set(cv2.CAP_PROP_FRAME_WIDTH, IMG_W)
    video.set(cv2.CAP_PROP_FRAME_HEIGHT, IMG_H)
    video.set(cv2.CAP_PROP_BRIGHTNESS, 20)
    video.set(cv2.CAP_PROP_CONTRAST, 45)
    video.set(cv2.CAP_PROP_SATURATION, 68)
    video.set(cv2.CAP_PROP_GAMMA, 400)
    video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('M', 'J', 'P', 'G'))
    # video.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('Y', 'U', 'Y', 'V'))
    video.set(cv2.CAP_PROP_FPS, 30)


def readFrame():
    global video
    suc, img = video.read()
    # suc = True
    if suc:
        img = img[140:-150, 420:-250]
        img = cv2.resize(
            img, (int(img.shape[1]/2), int(img.shape[0]/2)))
        return img

    return False

def closeCam():
    global video
    video.release()

