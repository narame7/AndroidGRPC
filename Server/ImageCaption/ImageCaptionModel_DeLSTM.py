
from keras.models import Sequential
from keras.models import Model
from keras.layers  import Input
from keras.layers import RepeatVector
from keras.layers import Merge, Dropout, merge
from keras.layers import LSTM, Activation
from keras.layers import Embedding
from keras.layers import Reshape, Input, Dense, Masking, Permute, TimeDistributed
from keras.optimizers import SGD, Adam, Nadam, RMSprop
from keras.layers.normalization import BatchNormalization
import numpy as np
from keras.layers.merge import Concatenate, Add


def GetImageCaptionModel(image_len, image_tstep, text_tstep, tok_num, embedding_matrix, weights_path=None):
    CNN_outDem = image_len
    one_dem = tok_num
    OUT_ONE_HOT_DEM = one_dem;
    
    emb_msize = (np.shape(embedding_matrix))

    left_branch = Sequential()
    left_branch.add(Reshape((image_len,),input_shape=( image_len,)))
    left_branch.add(RepeatVector(image_tstep))
       
    
    EMBEDDING_DIM = emb_msize[1]
    WORD_OUT_DEM = EMBEDDING_DIM
    MAX_SEQUENCE_LENGTH = text_tstep    
    MAX_NB_WORDS = tok_num    
    emb_size = np.shape(embedding_matrix)    
    nb_words = min(MAX_NB_WORDS, emb_size[0])    

    print("MAX_NB_WORDS : %d" % MAX_NB_WORDS)
    print("nb_words : %d" % nb_words)
    print("emb_size[0] : %d" % emb_size[0])
    print("MAX_SEQUENCE_LENGTH : %d" % MAX_SEQUENCE_LENGTH)
    
    right_branch = Sequential()
    
    #right_branch.add( Embedding(nb_words,
    #                        EMBEDDING_DIM,
    #                        weights=[embedding_matrix],
    #                        input_length=MAX_SEQUENCE_LENGTH,
    #                        trainable=False,
    #                        mask_zero=False))
   
    right_branch.add(Embedding(input_dim=nb_words, output_dim=1024, input_length=MAX_SEQUENCE_LENGTH))  
    
    #in_L = Input(shape=( image_len, ),name='image_input')
    #out_L1 = RepeatVector(image_tstep)(in_L);
    #decoder1_1 = Model(input=in_L, output=out_L1)    
    #in_R = Input(shape=( MAX_SEQUENCE_LENGTH,),name='text_input')    
    #out_R1 = Embedding(input_dim=nb_words, output_dim=512, input_length=MAX_SEQUENCE_LENGTH)(in_R)       
    #decoder1_2 = Model(input=in_R, output=out_R1)
    
    decoder = Sequential()
    #decoder.add(Merge([decoder1_1, decoder1_2], mode='concat'))    
    decoder.add(Merge([left_branch, right_branch], mode='concat'))    
    decoder.add(LSTM(1024, input_shape=(image_tstep, CNN_outDem+512), return_sequences=True, dropout_W=0.5, dropout_U=0.5, consume_less='gpu'))
    decoder.add(LSTM(1024, return_sequences=True, dropout_W=0.5, dropout_U=0.5, consume_less='gpu'))
    
    decoder.add(TimeDistributed(Dense(OUT_ONE_HOT_DEM, activation = 'softmax')))       
    #decoder.add(TimeDistributed(Dropout(0.5)))   
    
    
    sgd = SGD
    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.000)
    nadam = Nadam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, schedule_decay=0.001)
    decoder.compile(loss='categorical_crossentropy',
                     optimizer='sgd',
                     #optimizer='adam',
                     #optimizer='rmsprop',
                     metrics=['accuracy'])
    
    if weights_path:
        decoder.load_weights(weights_path)

    return(decoder)

def GetImageCaptionModel_ModAPI(image_len, image_tstep, text_tstep, tok_num, weights_path=None):
    CNN_outDem = image_len
    one_dem = tok_num
    OUT_ONE_HOT_DEM = one_dem;
    
    #emb_msize = (np.shape(embedding_matrix))

    in_L = Input(shape=( image_len, ),name='image_input')
    out_L1 = RepeatVector(image_tstep)(in_L);
    #out_L1 = TimeDistributed(Dense(image_len, activation ='relu'))(out_L1)
    #EMBEDDING_DIM = emb_msize[1]
    #WORD_OUT_DEM = EMBEDDING_DIM
    MAX_SEQUENCE_LENGTH = text_tstep    
    MAX_NB_WORDS = tok_num
    #emb_size = np.shape(embedding_matrix)    
    #nb_words = min(MAX_NB_WORDS, emb_size[0])    
    nb_words = MAX_NB_WORDS 

    print("MAX_NB_WORDS : %d" % MAX_NB_WORDS)
    print("nb_words : %d" % nb_words)    
    print("MAX_SEQUENCE_LENGTH : %d" % MAX_SEQUENCE_LENGTH)
    
    
    # Keras API previous 2.0 
    # in_R = Input(shape=( MAX_SEQUENCE_LENGTH,),name='text_input')
    # out_R1 = Embedding(input_dim=nb_words, output_dim=512, input_length=MAX_SEQUENCE_LENGTH)(in_R)    
    # out_m1 = merge([out_L1, out_R1], mode='concat')         
    # x_out1 = LSTM(1024, return_sequences=True, consume_less='gpu')(out_m1)       
    # #x_out2 = LSTM(1024, return_sequences=True,  consume_less='gpu')(x_out1)
    # x_out4 = TimeDistributed(Dense(OUT_ONE_HOT_DEM, activation ='relu'))(x_out1)
    # out_T3 = TimeDistributed(Dense(OUT_ONE_HOT_DEM, activation ='softmax'))(x_out4)
    # decoder = Model(input=[in_L,in_R], output=out_T3)

    # Keras API 2.0
    in_R = Input(shape=( MAX_SEQUENCE_LENGTH,),name='text_input')
    out_R1 = Embedding(input_dim=nb_words, output_dim=2048, trainable=True, input_length=MAX_SEQUENCE_LENGTH)(in_R)   
    #out_R1 = Embedding(nb_words, EMBEDDING_DIM, weights=[embedding_matrix], input_length=MAX_SEQUENCE_LENGTH, trainable=True, mask_zero=False)(in_R)  
    #out_R1 = Dense(512)(out_R1)
    #out_m1 = merge([out_L1, out_R1], mode='concat')     
    

    
    out_m1 = Concatenate()([out_L1, out_R1])     
    x_out1 = LSTM(512, return_sequences=True, implementation=2, dropout_W=0.5, dropout_U=0.5)(out_m1)   
    x_out0_1 = LSTM(256, return_sequences=True, implementation=2, dropout_W=0.5, dropout_U=0.5)(x_out1) 
    x_out0_2 = LSTM(128, return_sequences=True, implementation=2, dropout_W=0.5, dropout_U=0.5)(x_out0_1)     
    x_out0 = LSTM(256, return_sequences=True, implementation=2, dropout_W=0.5, dropout_U=0.5)(x_out0_2) 
    out_add1 = Add()([x_out0_1, x_out0])  
    x_out2 = LSTM(512, return_sequences=True,  implementation=2, dropout_W=0.5, dropout_U=0.5)(out_add1)
    out_T3 = TimeDistributed(Dense(OUT_ONE_HOT_DEM, activation ='softmax'))(x_out2) 
  
    '''
    out_m1 = Concatenate()([out_L1, out_R1])     
    x_out1 = LSTM(1024, return_sequences=True, implementation=2, dropout_W=0.5, dropout_U=0.5)(out_m1)      
    #x_out2 = LSTM(512, return_sequences=True, implementation=2, dropout_W=0.5, dropout_U=0.5)(x_out1)  
    #x_out3 = LSTM(512, return_sequences=True, implementation=2, dropout_W=0.5, dropout_U=0.5)(x_out2)  
    x_out4 = LSTM(1024, return_sequences=True, implementation=2, dropout_W=0.5, dropout_U=0.5)(x_out1)  
    out_T3 = TimeDistributed(Dense(OUT_ONE_HOT_DEM, activation ='softmax'))(x_out4)    
    '''
    
    #x_out3 = TimeDistributed(Dense(OUT_ONE_HOT_DEM, activation ='relu'))(x_out2)

    
    
    #out_D_T3 = TimeDistributed(Dropout(0.5))(out_T3)
    decoder = Model(inputs=[in_L,in_R], outputs = out_T3)
 

    sgd = SGD
    adam = Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, decay=0.000)
    nadam = Nadam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-08, schedule_decay=0.001)    
    decoder.compile(loss='categorical_crossentropy',
                     #optimizer='sgd',
                     optimizer='adam',
                     #optimizer='rmsprop',
                     metrics=['accuracy'])
    if weights_path:
        decoder.load_weights(weights_path)
    
    return(decoder)
