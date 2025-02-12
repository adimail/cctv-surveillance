import os
import sys
import cv2
import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import Xception
from tensorflow.keras.layers import (Input, Dense, Dropout, Bidirectional, LSTM,
                                     TimeDistributed)
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as K

if not os.path.exists('model'):
    os.makedirs('model')

if not (os.path.exists("data/fight") and os.path.exists("data/noFight")):
    print("Data not available for training: 'data/fight' and/or 'data/noFight' directory not found.")
    print("Please get the dataset from the repository: https://github.com/seymanurakti/fight-detection-surv-dataset")
    print("\nFollow these steps:")
    print("1. Run: rm -rf /content/fight-detection-surv-dataset")
    print("2. Run: rm -rf /content/data")
    print("3. Run: git clone https://github.com/seymanurakti/fight-detection-surv-dataset")
    print("4. Run: mkdir -p /content/data")
    print("5. Run: mv /content/fight-detection-surv-dataset/fight /content/data/")
    print("6. Run: mv /content/fight-detection-surv-dataset/noFight /content/data/")
    print("7. Run: rm -rf /content/fight-detection-surv-dataset")
    print("8. Run: ls /content/data  (should list: fight  noFight)")
    sys.exit(1)

fight_videos = sorted([f"data/fight/{video}" for video in os.listdir("data/fight/") if video.endswith(".mp4")])
nofight_videos = sorted([f"data/noFight/{video}" for video in os.listdir("data/noFight/") if video.endswith(".mp4")])
if len(fight_videos) == 0 or len(nofight_videos) == 0:
    print("Data not available for training: No video files found in one or both directories ('data/fight' or 'data/noFight').")
    sys.exit(1)

print(f"Found {len(fight_videos)} fight videos and {len(nofight_videos)} noFight videos.")


# ------------------
# Helper Functions
# ------------------

def sample_frames(video_path, num_frames=10):
    """
    Uniformly sample num_frames from the video located at video_path.
    Returns a numpy array of sampled frames.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error opening video: {video_path}")
        return np.array([])
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames < num_frames:
        cap.release()
        return np.array([])
    indices = np.linspace(0, total_frames - 1, num_frames, dtype=int)
    frames = []
    for i in range(total_frames):
        ret, frame = cap.read()
        if not ret:
            break
        if i in indices:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (299, 299))
            frames.append(frame)
    cap.release()
    return np.array(frames)

def preprocess_frames(frames):
    """
    Preprocess frames for the Xception network.
    Xception expects pixel values in the range [-1, 1].
    """
    frames = tf.keras.applications.xception.preprocess_input(frames.astype(np.float32))
    return frames

# ---------------------------
# Custom Attention Layer
# ---------------------------

class AttentionLayer(tf.keras.layers.Layer):
    def __init__(self, **kwargs):
        super(AttentionLayer, self).__init__(**kwargs)

    def build(self, input_shape):
        feature_dim = input_shape[-1]
        self.W = self.add_weight(name="att_weight",
                                 shape=(feature_dim, feature_dim),
                                 initializer="glorot_uniform",
                                 trainable=True)
        self.b = self.add_weight(name="att_bias",
                                 shape=(feature_dim,),
                                 initializer="zeros",
                                 trainable=True)
        self.u = self.add_weight(name="context_vector",
                                 shape=(feature_dim, 1),
                                 initializer="glorot_uniform",
                                 trainable=True)
        super(AttentionLayer, self).build(input_shape)

    def call(self, inputs):
        u_it = tf.nn.tanh(tf.tensordot(inputs, self.W, axes=1) + self.b)
        att = tf.tensordot(u_it, self.u, axes=1)
        att = tf.squeeze(att, axis=-1)
        att_weights = tf.nn.softmax(att, axis=1)
        att_weights_expanded = tf.expand_dims(att_weights, axis=-1)
        weighted_input = inputs * att_weights_expanded
        output = tf.reduce_sum(weighted_input, axis=1)
        return output

# ---------------------------
# Model Building Function
# ---------------------------

def build_model(num_frames=10, num_classes=2, lstm_units=50, dense_units=1024, use_attention=True):
    input_seq = Input(shape=(num_frames, 299, 299, 3))
    base_cnn = Xception(weights='imagenet', include_top=False, pooling='avg', input_shape=(299,299,3))
    base_cnn.trainable = False
    td_cnn = TimeDistributed(base_cnn)(input_seq)
    bi_lstm = Bidirectional(LSTM(lstm_units, return_sequences=True))(td_cnn)
    if use_attention:
        attention_out = AttentionLayer()(bi_lstm)
    else:
        attention_out = tf.reduce_mean(bi_lstm, axis=1)
    fc1 = Dense(dense_units, activation='relu')(attention_out)
    fc1 = Dropout(0.5)(fc1)
    fc2 = Dense(50, activation='relu')(fc1)
    output = Dense(num_classes, activation='softmax')(fc2)
    model = Model(inputs=input_seq, outputs=output)
    return model

# ---------------------------
# Data Generator Functions
# ---------------------------

def video_generator(video_paths, label, batch_size=4, num_frames=10):
    """
    A generator that yields batches of (X, y) from a list of video file paths.
    """
    while True:
        np.random.shuffle(video_paths)
        for i in range(0, len(video_paths), batch_size):
            batch_paths = video_paths[i:i+batch_size]
            batch_data = []
            for path in batch_paths:
                frames = sample_frames(path, num_frames=num_frames)
                if frames.shape[0] != num_frames:
                    continue  # Skip videos without enough frames
                frames = preprocess_frames(frames)
                batch_data.append(frames)
            if batch_data:
                X = np.array(batch_data)
                y = np.array([label for _ in range(len(batch_data))])
                idx = np.arange(X.shape[0])
                np.random.shuffle(idx)
                yield X[idx], y[idx]

def combined_generator(fight_gen, nofight_gen):
    while True:
        X1, y1 = next(fight_gen)
        X2, y2 = next(nofight_gen)
        X_batch = np.concatenate([X1, X2], axis=0)
        y_batch = np.concatenate([y1, y2], axis=0)
        idx = np.arange(X_batch.shape[0])
        np.random.shuffle(idx)
        yield X_batch[idx], y_batch[idx]

# ---------------------------
# Load Video Paths and Labels
# ---------------------------

fight_label = [1, 0]
nofight_label = [0, 1]
batch_size = 4
num_frames = 10

fight_gen = video_generator(fight_videos, fight_label, batch_size=batch_size, num_frames=num_frames)
nofight_gen = video_generator(nofight_videos, nofight_label, batch_size=batch_size, num_frames=num_frames)
train_gen = combined_generator(fight_gen, nofight_gen)

# ---------------------------
# Build and Train the Model
# ---------------------------

model = build_model(num_frames=num_frames, use_attention=True)
model.compile(optimizer=Adam(learning_rate=1e-4), loss='mean_squared_error', metrics=['accuracy'])
model.summary()

history = model.fit(train_gen, steps_per_epoch=10, epochs=15)

model.save('model/fight_detection_model.h5')
print("Model saved to model/fight_detection_model.h5")
