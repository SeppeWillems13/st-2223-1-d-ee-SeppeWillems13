import os


def remove_common_files(dir1, dir2):
    # List all the files in both directories
    files1 = os.listdir(dir1)
    files2 = os.listdir(dir2)

    # Find the common files
    common_files = set(files1) & set(files2)

    # Remove the common files from dir1
    for file in common_files:
        file_path = os.path.join(dir1, file)
        os.remove(file_path)


if __name__ == '__main__':
    gets_removed_here = input("original dir FILES WILL BE DELETED:")
    checks_here = input("check this dir for duplicates:")
    if not os.path.isdir(gets_removed_here) or not os.path.isdir(checks_here):
        print("Error: one or both of the directories do not exist or are not accessible.")
    else:
        remove_common_files(gets_removed_here, checks_here)
