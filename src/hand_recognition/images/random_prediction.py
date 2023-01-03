import os
import random
import shutil


class random_prediction:
    def __init__(self, paper_dir, scissors_dir, rock_dir, prediction_dir):
        self.paper_dir = paper_dir
        self.scissors_dir = scissors_dir
        self.rock_dir = rock_dir
        self.prediction_dir = prediction_dir

    def shuffle_and_save_images(self):
        # Create the prediction_dir directory if it doesn't already exist
        if not os.path.exists(self.prediction_dir):
            os.makedirs(self.prediction_dir)

        # Get a list of all the file names in the paper_dir, scissors_dir, and rock_dir
        paper_filenames = os.listdir(self.paper_dir)
        scissors_filenames = os.listdir(self.scissors_dir)
        rock_filenames = os.listdir(self.rock_dir)

        # Shuffle the file names
        random.shuffle(paper_filenames)
        random.shuffle(scissors_filenames)
        random.shuffle(rock_filenames)

        # Select the first 100 file names from each list
        paper_filenames = paper_filenames[:100]
        scissors_filenames = scissors_filenames[:100]
        rock_filenames = rock_filenames[:100]

        # Copy the files to the prediction_dir
        for filename in paper_filenames:
            shutil.copy(os.path.join(self.paper_dir, filename), self.prediction_dir)
        for filename in scissors_filenames:
            shutil.copy(os.path.join(self.scissors_dir, filename), self.prediction_dir)
        for filename in rock_filenames:
            shutil.copy(os.path.join(self.rock_dir, filename), self.prediction_dir)


# Set the directories where the images are located
paper_dir = '../image_data/paper'
scissors_dir = '../image_data/scissors'
rock_dir = '../image_data/rock'

# Set the directory where the shuffled images will be saved
prediction_dir = 'prediction_unlabeled_images'

# Create an instance of the ImageShuffler class
image_shuffler = random_prediction(paper_dir, scissors_dir, rock_dir, prediction_dir)

# Call the shuffle_and_save_images method
image_shuffler.shuffle_and_save_images()
