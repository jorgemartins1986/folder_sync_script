import os
from os import listdir
from os.path import isfile, join, isdir
import shutil
import filecmp
import sys
import time
import logging

from pathlib import Path

# gets a list with the path from all subfolders recursively
def get_subfolders_path(dirname):
    subfolders= [ f.path for f in os.scandir(dirname) if f.is_dir() ]
    for dirname in list(subfolders):
        subfolders.extend(get_subfolders_path(dirname))
    return subfolders

# removes all files from replica that are not present on original folder
def remove_files_from_replica(original_path, replica_path):
    logger = logging.getLogger(__name__)

    # gets all the files names from the original and replica folder
    file_names_from_original = [file for file in listdir(original_path) if isfile(join(original_path, file))]
    file_names_from_replica = [file for file in listdir(replica_path) if isfile(join(replica_path, file))]

    # tests to see if replica folder has any file with a name that it's not in the original folder
    # if it finds one then deletes it
    for file in file_names_from_replica:
        if (file not in file_names_from_original):
            replica_file = replica_path + "\\" + str(file)
            try:
                os.remove(replica_file)
                logger.info("{} was removed from {}".format(file, replica_path))
                print("{} was removed from {}".format(file, replica_path))
            except OSError as e:
                logger.error("Could not remove file {} from {} with due to ERROR: {}".format(file, replica_path, str(e)))
                print("Could not remove file {} from {} with due to ERROR: {}".format(file, replica_path, str(e)))

# adds a file if it's not on replica folder but is on original folder or updates it if it's different
def add_or_update_file(original_path, replica_path):
    logger = logging.getLogger(__name__)

    # gets all the files names from the original and replica folder
    file_names_from_original = [file for file in listdir(original_path) if isfile(join(original_path, file))]
    file_names_from_replica = [file for file in listdir(replica_path) if isfile(join(replica_path, file))]

    # tests to see if a file from the original folder is on the replica folder
    for file in file_names_from_original:
        if (file not in file_names_from_replica):
            # if the file is not on the replica folder it copies it
            file_to_copy = original_path + "\\" + str(file)
            try:
                shutil.copy2(file_to_copy, replica_path)
                logger.info("{} was copied from {} to {}".format(file, original_path, replica_path))
                print("{} was copied from {} to {}".format(file, original_path, replica_path))
            except IOError as e:
                logger.error("Could not copy file {} from {} to {} with due to ERROR: {}".format(file, original_path, replica_path, str(e)))
                print("Could not copy file {} from {} to {} with due to ERROR: {}".format(file, original_path, replica_path, str(e)))
        else:
            # in case it's in the folder it does a byte comparison to see if it's exactly the same file and
            # if it's not it updates the file in the replica folder to the correct one
            original_file = original_path + "\\" + str(file)
            replica_file = replica_path + "\\" + str(file)
            if (filecmp.cmp(original_file, replica_file, shallow=False) == False):
                try:
                    shutil.copy2(original_file, replica_path)
                    logger.info("{} was updated to latest version in folder {}".format(file, replica_path))
                    print("{} was updated to latest version in folder {}".format(file, replica_path))
                except IOError as e:
                    logger.error("Could not update file {} in {} due to ERROR: {}".format(file, replica_path, str(e)))
                    print("Could not update file {} in {} due to ERROR: {}".format(file, replica_path, str(e)))

def main(args):
    
    # tests if all 4 required arguments are present and if not informs the user of the correct way to invoke the script
    if(len(args) != 4):
        print("You must pass exactly 4 parameters for this script.")
        print("Syntax should look like:")
        print("python folder_sync.py <original folder path> <replica_folder_path> <time period repetition> <log file path>")
    else:
        #gets original, replica folder, time interval and log file path from the args
        original_path = args[0]
        replica_path = args[1]
        sleeptime = int(args[2])
        log_file_path = args[3]
        
        logger = logging.getLogger(__name__)
        logging.basicConfig(filename=log_file_path, encoding='utf-8', level=logging.DEBUG)

        print("press Ctrl+C to exit.")

        subfolders = get_subfolders_path(original_path)

        while True:
            remove_files_from_replica(original_path, replica_path)
            add_or_update_file(original_path, replica_path)

            for folder in subfolders:
                replica_folder = folder.replace(original_path, replica_path)
                if Path(replica_folder).is_dir():
                    remove_files_from_replica(folder, replica_folder)
                    add_or_update_file(folder, replica_folder)
                else:
                    logger.info("{} was copied to replica {}".format(folder, replica_folder))
                    print("{} was copied to replica {}".format(folder, replica_folder))
                    shutil.copytree(folder, replica_folder) #copy folder with all subfolders and files

            # pauses the script until next execution
            time.sleep(sleeptime)

if __name__ == "__main__":
    args = sys.argv[1:]
    main(args)