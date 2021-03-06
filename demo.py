import numpy as np  
import sys,os  
import cv2
# caffe_root = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/'
# sys.path.insert(0, caffe_root + 'python')
sys.path.append('/media/ziwei/Harddisk02/HanBin/TOOL/workspace_caffe/ssd/python')
import caffe  

# # V1_3category(three categroy without_new)
# net_file= '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_3category/MobileNetSSD_deploy.prototxt'
# caffe_model='MobileNetSSD_deploy_zhb49000.caffemodel'
# test_dir = "images"

# # V1_2categroy(two categroy without_new)
# net_file= '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_2categroy/MobileNetSSD_deploy.prototxt'
# caffe_model='MobileNetSSDV1_deploy_without_new_0822.caffemodel'
# test_dir = "images"

# # V1_2categroy(two categroy with_new)
net_file= '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_4_sp/MobileNetSSD_deploy.prototxt'
caffe_model='0915_mobilenetv1_4_100000.caffemodel'
test_dir = "images"

# # V2
# net_file= '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V2/MobileNetSSDV2_deploy.prototxt'
# caffe_model='MobileNetSSDV2_deploy_3category_10000.caffemodel'
# test_dir = "images"

# # V2_4
# net_file= '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V2_4category/MobileNetSSDV2_deploy.prototxt'
# caffe_model='MobileNetSSDV2_4_deploy_50000.caffemodel'
# test_dir = "images"

# # V2_old
# net_file= '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/old_V2/MobileNetSSDV2_deploy.prototxt'
# caffe_model='old_V2/mobilenetv2_iter_300000.caffemodel'
# test_dir = "images"

if not os.path.exists(caffe_model):
    print("MobileNetSSD_deploy.caffemodel does not exist,")
    print("use merge_bn.py to generate it.")
    exit()
net = caffe.Net(net_file,caffe_model,caffe.TEST)  

CLASSES = ('background',
           'person'
           # ,'face'
            ,'car',
            'bicycle'
           )

# CLASSES = ('background',
#            'aeroplane', 'bicycle', 'bird', 'boat',
#            'bottle', 'bus', 'car', 'cat', 'chair',
#            'cow', 'diningtable', 'dog', 'horse',
#            'motorbike', 'person', 'pottedplant',
#             'sheep', 'sofa', 'train', 'tvmonitor'
#            )


def preprocess(src):
    img = cv2.resize(src, (300,300))
    img = img - 127.5
    img = img * 0.007843
    return img

def postprocess(img, out):   
    h = img.shape[0]
    w = img.shape[1]
    box = out['detection_out'][0,0,:,3:7] * np.array([w, h, w, h])

    cls = out['detection_out'][0,0,:,1]
    conf = out['detection_out'][0,0,:,2]
    print(cls,conf)
    return (box.astype(np.int32), conf, cls)

def detect(imgfile):
    origimg = cv2.imread(imgfile)
    img = preprocess(origimg)
    
    img = img.astype(np.float32)
    img = img.transpose((2, 0, 1))

    net.blobs['data'].data[...] = img
    out = net.forward()  
    box, conf, cls = postprocess(origimg, out)

    for i in range(len(box)):
       # if CLASSES[int(cls[i])] != 'person':
       #     continue
       p1 = (box[i][0], box[i][1])
       p2 = (box[i][2], box[i][3])
       cv2.rectangle(origimg, p1, p2, (0,255,0))
       p3 = (max(p1[0], 15), max(p1[1], 15))
       title = "%s:%.2f" % (CLASSES[int(cls[i])], conf[i])
       cv2.putText(origimg, title, p3, cv2.FONT_ITALIC, 0.6, (0, 255, 0), 1)
    cv2.imshow("SSD", origimg)
 
    k = cv2.waitKey(0) & 0xff
        #Exit if ESC pressed
    if k == 27 : return False
    return True

for f in os.listdir(test_dir):
    if detect(test_dir + "/" + f) == False:
       break
# f = '1111.jpg'
# detect(test_dir + "/" + f)
