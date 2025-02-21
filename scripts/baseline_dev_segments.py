import sys
import tensorflow as tf
import numpy as np
sys.path.insert(0, './scripts')
from tqdm import tqdm
import feature_tools as ft

#init params
NN_MODEL = 'lang2vec'
INPUT_DIM = 40
is_batchnorm = False
SOFTMAX_NUM = 17
nn_model = __import__(NN_MODEL)
FEAT_TYPE='mfcc'
N_FFT=400
HOP=160
VAD=True
CMVN='m'
DATA_ROOT='/Users/mac/Desktop/Master_topic/arabic_dialect_identification_v2/wav'

#prepare wav.scp for each data set. Set your $DATA_ROOT variable before run. 
lines = open('data/dev_segments/utt2lang').readlines()
fid = open('data/dev_segments/wav.scp','w')
for line in lines:
    cols = line.rstrip().split()
    fid.write('%s %s/dev_segments/%s.wav\n'%(cols[0], DATA_ROOT, cols[0]))
fid.close()


DATA_FOLDER='data/dev_segments'
lines = open('data/language_id_initial').readlines()

lang2idx = {}
for line in lines:
    lang = line.rstrip().split()[0]
    idx = line.rstrip().split()[1]
    lang2idx[lang]=int(idx)

wav_list = []
devid = []
lines=open(DATA_FOLDER+'/wav.scp').readlines()
for line in lines:
    cols = line.rstrip().split()
    devid.append(cols[0])
    wav_list.append(cols[1])

    
#feature extraction
feat, _, utt_shape, tffilename = ft.feat_extract(wav_list,FEAT_TYPE,N_FFT,HOP,VAD,CMVN,0)

#init placeholder
test_feat_batch = tf.compat.v1.placeholder(tf.float32, [None,None,np.int(INPUT_DIM)],name="test_feat_batch")
test_label_batch = tf.compat.v1.placeholder(tf.int32, [None],name="test_label_batch")
test_shape_batch = tf.compat.v1.placeholder(tf.int32, [None,2],name="test_shape_batch")

#init model
emnet_validation = nn_model.nn(test_feat_batch,test_label_batch,test_label_batch,test_shape_batch, SOFTMAX_NUM,False,INPUT_DIM,is_batchnorm);
tf.compat.v1.get_variable_scope().reuse_variables()
sess = tf.compat.v1.InteractiveSession()
saver = tf.compat.v1.train.Saver()
tf.compat.v1.initialize_all_variables().run()

#load pretrained model
RESUME_STARTPOINT = 7712000
saver.restore(sess,'data/pretrained_model/model'+str(RESUME_STARTPOINT)+'.ckpt-'+str(RESUME_STARTPOINT))

#extract output layer
output = []
for iter in tqdm(range(len(feat))):
    o1 = emnet_validation.o1.eval({test_feat_batch:[feat[iter]], test_shape_batch:[utt_shape[iter]]})
    output.extend([o1])
output = np.squeeze(output)

#write result file
fid = open('result_dev.csv','w')
for row in range(output.shape[0]):
    fid.write('%s'%devid[row])    
    for col in range(output.shape[1]):
        fid.write(',%f' % output[row,col])
    fid.write('\n')
fid.close()