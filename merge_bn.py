import numpy as np  
import sys,os  
# caffe_root = '/media/ziwei/Harddisk02/ziwei/SSD/caffe'
# sys.path.insert(0, caffe_root + 'python')
sys.path.append('/media/ziwei/Harddisk02/ziwei/SSD/caffe/python')
import caffe  

# mobilenet V1_3category without new
# train_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_3category/MobileNetSSD_train.prototxt'
# train_model = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/snapshot_V1/mobilenet_iter_49000.caffemodel'  #should be your snapshot caffemodel
# deploy_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_3category/MobileNetSSD_deploy.prototxt'
# save_model = 'MobileNetSSD_deploy_zhb49000.caffemodel'

# # mobilenet V1_2category without new
# train_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_2category/MobileNetSSD_train.prototxt'
# train_model = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/snapshot_V1/0822_without_new_mobilenet_iter_30000.caffemodel'  #should be your snapshot caffemodel
# deploy_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_2category/MobileNetSSD_deploy.prototxt'
# save_model = 'MobileNetSSDV1_deploy_without_new_0822.caffemodel'

# # mobilenet V1_4category with new
train_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_4_sp/MobileNetSSD_train.prototxt'
train_model = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/snapshot_V1_4/mobilenet_iter_9660.caffemodel'  #should be your snapshot caffemodel
deploy_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V1_4_sp/MobileNetSSD_deploy.prototxt'
save_model = '0915_mobilenetv1_4_100000.caffemodel'

# mobilenet V2
# train_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V2/MobileNetSSDV2_train.prototxt'
# train_model = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/snapshot_V2_3/0904_mobilenet_iter_9999.caffemodel'  #should be your snapshot caffemodel
# deploy_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V2/MobileNetSSDV2_deploy.prototxt'
# save_model = 'MobileNetSSDV2_deploy_3category_10000.caffemodel'

# mobilenet V2_4category
# train_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V2_4category/MobileNetSSDV2_train.prototxt'
# train_model = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/snapshot_V2_4/0829_mobilenet_iter_19998.caffemodel'  #should be your snapshot caffemodel
# deploy_proto = '/media/ziwei/Harddisk02/ziwei/SSD/caffe/examples/MobileNet-SSD-zhb/example/V2_4category/MobileNetSSDV2_deploy.prototxt'
# save_model = 'MobileNetSSDV2_4_deploy_20001.caffemodel'

def merge_bn(net, nob):
    '''
    merge the batchnorm, scale layer weights to the conv layer, to  improve the performance
    var = var + scaleFacotr
    rstd = 1. / sqrt(var + eps)
    w = w * rstd * scale
    b = (b - mean) * rstd * scale + shift
    '''
    for key in net.params:
        if type(net.params[key]) is caffe._caffe.BlobVec:
            if key.endswith("/bn") or key.endswith("/scale"):
                continue
            else:
                conv = net.params[key]
                if key + "/bn" not in net.params:
                    for i, w in enumerate(conv):
                        nob.params[key][i].data[...] = w.data
                else:
                    bn = net.params[key + "/bn"]
                    scale = net.params[key + "/scale"]
                    wt = conv[0].data
                    channels = wt.shape[0]
                    bias = np.zeros(wt.shape[0])
                    if len(conv) > 1:
                        bias = conv[1].data
                    mean = bn[0].data
                    var = bn[1].data
                    scalef = bn[2].data

                    scales = scale[0].data
                    shift = scale[1].data

                    if scalef != 0:
                        scalef = 1. / scalef
                    mean = mean * scalef
                    var = var * scalef
                    rstd = 1. / np.sqrt(var + 1e-5)
                    rstd1 = rstd.reshape((channels,1,1,1))
                    scales1 = scales.reshape((channels,1,1,1))
                    wt = wt * rstd1 * scales1
                    bias = (bias - mean) * rstd * scales + shift
                    
                    nob.params[key][0].data[...] = wt
                    nob.params[key][1].data[...] = bias
  

net = caffe.Net(train_proto, train_model, caffe.TRAIN)  
net_deploy = caffe.Net(deploy_proto, caffe.TEST)  

merge_bn(net, net_deploy)
net_deploy.save(save_model)

