from FaceRec import CyPi_FaceRecognition
import threading



if __name__ == '__main__':

    CyPi_FaceRecognition.emitter.on('test2', print('I GOT THE EVENT'))
    CyPi_FaceRecognition.main()


