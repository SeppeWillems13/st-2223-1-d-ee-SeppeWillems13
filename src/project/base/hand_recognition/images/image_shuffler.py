import os
import random
import shutil


class image_shuffler:
    def __init__(self, image_dir, train_dir, test_dir):
        self.image_dir = image_dir
        self.train_dir = train_dir
        self.test_dir = test_dir

    def split_data(self):
        # Create the directories for the training and test sets if they don't exist
        if not os.path.exists(self.train_dir):
            os.makedirs(self.train_dir)

        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)

        # List the directories for each class
        class_dirs = [os.path.join(self.image_dir, x) for x in os.listdir(self.image_dir) if
                      os.path.isdir(os.path.join(self.image_dir, x))]

        # Shuffle the directories
        random.shuffle(class_dirs)

        # Iterate over the directories
        for class_dir in class_dirs:
            # Get the class label from the directory name
            label = os.path.basename(class_dir)

            # Set the directories for the training and test splits for this class
            train_class_dir = os.path.join(self.train_dir, label)
            test_class_dir = os.path.join(self.test_dir, label)

            # Create the directories for the training and test splits if they don't exist
            if not os.path.exists(train_class_dir):
                os.makedirs(train_class_dir)

            if not os.path.exists(test_class_dir):
                os.makedirs(test_class_dir)

            # List the images in the current class directory
            image_paths = [os.path.join(class_dir, x) for x in os.listdir(class_dir)]

            # Shuffle the images
            random.shuffle(image_paths)

            # Calculate the number of images to put in the training and test sets
            num_train = int(0.7 * len(image_paths))
            len(image_paths) - num_train

            # Split the images into the training and test sets
            train_images = image_paths[:num_train]
            test_images = image_paths[num_train:]

            counter_train = 0
            counter_test = 0
            # Copy the images to the appropriate directories
            for image_path in train_images:
                counter_train += 1
                print('training_image:' + str(counter_train))
                shutil.copy(image_path, train_class_dir)

            for image_path in test_images:
                counter_test += 1
                print('test_image:' + str(counter_test))
                shutil.copy(image_path, test_class_dir)


# Set the directories for the training and test sets
train_dir = 'train'
test_dir = 'test'
image_dir = '../new_image_data'

# Create an instance of the DataSplitter class
splitter = image_shuffler(image_dir, train_dir, test_dir)

# Split the data
splitter.split_data()
