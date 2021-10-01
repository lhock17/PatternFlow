import tensorflow as tf
from tensorflow.keras.preprocessing import image_dataset_from_directory
import matplotlib.pyplot as plt
from model import train, Perceiver

# Constants
IMAGE_DIR = 's4571730/AKOA_Analysis'
BATCH_SIZE = 32
IMG_SIZE = (260, 228)
ROWS, COLS = IMG_SIZE[0], IMG_SIZE[1]
IMG_SHAPE = (*(IMG_SIZE), 3)
TEST_PORTION = 5
SHUFFLE_RATE = 512
AUTO_TUNE = tf.data.experimental.AUTOTUNE

"""
Create train, validate and test dataset
Images have to be in left and right folders 

    AKOA_Analysis/
    ...left/
    ......left_image_1.jpg
    ......left_image_2.jpg
    ...right/
    ......right_image_1.jpg
    ......right_image_2.jpg

"""
def create_dataset(image_dir, batch_size, img_size):
    # Training dataset, shuffle is True by default
    training_dataset = image_dataset_from_directory(image_dir, validation_split=0.2, color_mode='grayscale',
                                                    subset="training", seed=46, label_mode='int',
                                                    batch_size=batch_size, image_size=img_size)
    # Validation dataset
    validation_dataset = image_dataset_from_directory(image_dir, validation_split=0.2, color_mode='grayscale',
                                                      subset="validation", seed=46, label_mode='int',
                                                      batch_size=batch_size, image_size=img_size)

    # Test dataset, taking 1/5 of the validation set
    val_batches = tf.data.experimental.cardinality(validation_dataset)
    test_dataset = validation_dataset.take(val_batches // TEST_PORTION)
    validation_dataset = validation_dataset.skip(val_batches // TEST_PORTION)

    # normalize and prefetch images for faster training
    training_dataset = training_dataset.map(process).prefetch(AUTO_TUNE)
    validation_dataset = validation_dataset.map(process).prefetch(AUTO_TUNE)
    test_dataset = test_dataset.map(process).prefetch(AUTO_TUNE)

    return training_dataset, validation_dataset, test_dataset

"""
Normalize image to range [0,1]
"""
def process(image,label):
    image = tf.cast(image / 255. ,tf.float32)
    return image,label

def runner_code():
    pass

if __name__ == "__main__":

    # generate dataset
    training_set, validation_set, test_set = create_dataset(IMAGE_DIR, BATCH_SIZE, IMG_SIZE)

    for image, label in training_set:
        # train_image = image[0]
        # b, *axis, _ = image.shape
        # axis_pos = list(map(lambda size: tf.linspace(-1.0, 1.0, num=size), axis))
        # pos = tf.stack(tf.meshgrid(*axis_pos, indexing="ij"), axis=-1)
        # encode = fourier_encode(pos, 4, 10)
        # print(encode.shape)
        break


    LATENT_SIZE = 256  # Size of the latent array.
    NUM_BANDS = 4
    PROJ_SIZE = 2*(2*NUM_BANDS + 1) + 1  # Projection size of data after fourier encoding
    NUM_HEADS = 8  # Number of Transformer heads.
    DENSE_UNITS = [
        PROJ_SIZE,
        PROJ_SIZE,
    ]  # Size of the Transformer Feedforward network.
    NUM_TRANS_BLOCKS = 4
    NUM_ITER = 2  # Repetitions of the cross-attention and Transformer modules.
    CLASSIFIER_UNITS = [
        PROJ_SIZE,
        2,
    ]  # Size of the Feedforward network of the final classifier.
    MAX_FREQ = 10
    LR = 0.0001
    WEIGHT_DECAY = 0.0001
    EPOCHS = 10
    START_EPOCH = tf.Variable(1)

    # Initialize the model
    knee_model = Perceiver(patch_size=0,
                            data_size=ROWS*COLS, 
                            latent_size=LATENT_SIZE,
                            num_bands=NUM_BANDS,
                            proj_size=PROJ_SIZE, 
                            num_heads=NUM_HEADS,
                            num_transformer_blocks=NUM_TRANS_BLOCKS,
                            dense_layers=DENSE_UNITS,
                            num_iterations=NUM_ITER,
                            classifier_units=CLASSIFIER_UNITS,
                            max_freq=MAX_FREQ,
                            lr=LR,
                            weight_decay=WEIGHT_DECAY,
                            epoch=EPOCHS)

   

    checkpoint_dir = './ckpts'

    # if not EVAL_ONLY:
    history = train(knee_model,
                    train_set=training_set,
                    val_set=validation_set,
                    test_set=test_set,

                    )

    knee_model.save(checkpoint_dir)


    # # Train the model
    # history_data = knee_model.train_knee_classifier()

    # # Test set evaluation
    # knee_model.model_evaluation(eval_type='final')

    # # View model summary
    # knee_model.get_model_summary(model_type='complete')

    # # Plotting the Learning curves
    # acc = history_data.history['accuracy']
    # val_acc = history_data.history['val_accuracy']

    # loss = history_data.history['loss']
    # val_loss = history_data.history['val_loss']

    # plt.figure(figsize=(8, 8))
    # plt.subplot(2, 1, 1)
    # plt.plot(acc, label='Training Accuracy')
    # plt.plot(val_acc, label='Validation Accuracy')
    # plt.legend(loc='lower right')
    # plt.ylabel('Accuracy')
    # plt.ylim([min(plt.ylim()), 1])
    # plt.title('Training and Validation Accuracy')

    # plt.subplot(2, 1, 2)
    # plt.plot(loss, label='Training Loss')
    # plt.plot(val_loss, label='Validation Loss')
    # plt.legend(loc='upper right')
    # plt.ylabel('Cross Entropy')
    # plt.ylim([0, 1.0])
    # plt.title('Training and Validation Loss')
    # plt.xlabel('epoch')
    # plt.show()

    # # Compare predicted and class labels

    # # Retrieve a batch of images from the test set
    # image_batch, label_batch = test_set.as_numpy_iterator().next()
    # predictions = knee_model.complete_model.predict_on_batch(image_batch).flatten()

    # # Apply a sigmoid since our model returns logits
    # predictions = tf.nn.sigmoid(predictions)
    # predictions = tf.where(predictions < 0.5, 0, 1)

    # print('Predictions:\n', predictions.numpy())
    # print('Labels:\n', label_batch)

    # plt.figure(figsize=(10, 10))
    # for i in range(9):
    #     ax = plt.subplot(3, 3, i + 1)
    #     plt.imshow(image_batch[i].astype("uint8"))
    #     plt.title(class_names[predictions[i]])
    #     plt.axis("off")


