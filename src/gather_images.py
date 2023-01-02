import cv2
import os
import sys


def collect_images(label_name, num_samples):
    # Set up the save path and create the directory if it doesn't exist
    save_path = os.path.join('image_data', label_name)
    os.makedirs(save_path, exist_ok=True)

    # Initialize the camera and set up the video capture
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error opening video stream or file")
        return

    start = False
    count = 0

    while True:
        # Capture the frame from the camera
        ret, frame = cap.read()
        if not ret:
            print("Error reading frame")
            break

        # Check if we have reached the target number of samples
        if count == num_samples:
            break

        # Draw the rectangle and collect the images if the "start" flag is set
        cv2.rectangle(frame, (100, 100), (500, 500), (255, 255, 255), 2)
        if start:
            roi = frame[100:500, 100:500]
            save_path = os.path.join(save_path, '{}.jpg'.format(count + 1))
            cv2.imwrite(save_path, roi)
            count += 1

        # Display the video frame and the count
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, f"Collecting {count}", (5, 50), font, 0.7, (0, 255, 255), 2, cv2.LINE_AA)
        cv2.imshow("Collecting images", frame)

        # Check for user input
        k = cv2.waitKey(10)
        if k == ord('a'):
            start = not start
        elif k == ord('q'):
            break

    # Release the camera and destroy the window
    cap.release()
    cv2.destroyAllWindows()
    print(f"\n{count} image(s) saved to {save_path}")


def main():
    # Parse the command-line arguments
    try:
        label_name = sys.argv[1]
        num_samples = int(sys.argv[2])
    except:
        print("Error: missing or invalid arguments")
        print("Usage: python collect_images.py LABEL_NAME NUM_SAMPLES")
        return

    # Collect the images
    collect_images(label_name, num_samples)


if __name__ == '__main__':
    main()
