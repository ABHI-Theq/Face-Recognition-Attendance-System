import cv2
import os
import face_recognition
import pickle

import firebase_admin
from firebase_admin import credentials, storage
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKeyACCountTYPE.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':'DATABASE_URL',
    'storageBucket':'STORAGE_URL'
})


folderPath='Images'
imglist=os.listdir(folderPath)
print(imglist)
personImg=[]
studentId=[]
for path in imglist:
    personImg.append(cv2.imread(os.path.join(folderPath,path)))
    print(path.split('.')[0])
    studentId.append(path.split('.')[0])

    fileName=f"{folderPath}/{path}"
    bucket=storage.bucket()
    bloby=bucket.blob(fileName)
    bloby.upload_from_filename(fileName)

print(studentId)
def findEncodings(imagesList):
    encodeList=[]
    for img in imagesList:
        img=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode=face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

    return encodeList

print("Encoding Started..")
encodeListKnown=findEncodings(personImg)
encodeListKnownwithId=[encodeListKnown,studentId]
# print(encodeListKnown)
print("Encoding completed")

with open("EncodingFile.p","wb") as f:
    pickle.dump(encodeListKnownwithId,f)
    print("File saved")
