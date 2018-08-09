import numpy as np
import cv2 as cv
face_cascade = cv.CascadeClassifier('/home/lewis/gitRepos/face_tagger/haar.xml')
# eye_cascade = cv.CascadeClassifier('haarcascade_eye.xml')
img = cv.imread('/home/lewis/test_imgs/DSC_9847.JPG')
# img.shape  
# gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
# # cv.namedWindow("main", cv.WINDOW_AUTOSIZE)

# faces = face_cascade.detectMultiScale(gray, 1.3, 3)
# for (x,y,w,h) in faces:
#     print 'hay'
#     print x, y, w, h
#     cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0),8)
#     roi_gray = gray[y:y+h, x:x+w]
#     roi_color = img[y:y+h, x:x+w]
    # eyes = eye_cascade.detectMultiScale(roi_gray)
    # for (ex,ey,ew,eh) in eyes:
    #     cv.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
# face_cascade = cv.CascadeClassifier('/home/lewis/haarside.xml')

# faces = face_cascade.detectMultiScale(gray, 1.3, 3)
# for (x,y,w,h) in faces:
#     print 'hay side'
#     print x, y, w, h
#     cv.rectangle(img,(x,y),(x+w,y+h),(255,160,12),8)
#     roi_gray = gray[y:y+h, x:x+w]
#     roi_color = img[y:y+h, x:x+w]


img = cv.resize(img, (img.shape[1] / 6, img.shape[0]/ 6))
cv.imshow('img',img)
a = chr(cv.waitKey(0) & 0xFF)
cv.destroyAllWindows()
