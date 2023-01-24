# import the necessary packages
import os

import cv2
from keras.models import load_model

test_image_path = r"C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\base\hand_recognition\image_data\image_test\paper"

model_path = r"C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\keras\keras_model_third.h5"
label_binarizer_path = r"C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\keras\labels.txt"

#for all images in the test folder
for image_path in os.listdir(test_image_path):
    print("image_path", image_path)
    image = cv2.imread(test_image_path +'\\' + image_path)
    output = image.copy()
    image = cv2.resize(image, (32, 32))

    # scale the pixel values to [0, 1]
    image = image.astype("float") / 255.0
    image = image.flatten()
    print("image after flattening", len(image))
    image = image.reshape((1, image.shape[0]))
    print("image--reshape", image.shape)

    # load the model and label binarizer
    print("[INFO] loading network and label binarizer...")
    model = load_model(model_path)
    labels_path = r"C:\Users\seppe\PycharmProjects\st-2223-1-d-ee-SeppeWillems13\src\project\keras\labels.txt"

    with open(labels_path, 'r') as f:
        labels = f.read().splitlines()

    # # make a prediction on the image
    print(image.shape)
    preds = model.predict(image)

    # find the class label index with the largest corresponding
    # probability
    print("preds.argmax(axis=1)", preds.argmax(axis=1))
    i = preds.argmax(axis=1)[0]
    print(i)
    label = labels[i]

    # draw the class label + probability on the output image
    text = "{}: {:.2f}%".format(label, preds[0][i] * 100)
    cv2.putText(output, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                (0, 0, 255), 2)

    # show the output image
    cv2.imshow("Image", output)
    cv2.waitKey(0)
