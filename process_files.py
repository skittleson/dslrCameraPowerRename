import shutil
import wmi
import os
from time import strftime, localtime
c = wmi.WMI()


def copy(src) -> int:
    """ Copy all files in camera directory to users directoy for human processing
    """
    dst = os.path.join(os.path.expanduser('~'), "a6000Temp")
    if os.path.isdir(dst):
        print("found existing temp folder, delete it")
        shutil.rmtree(dst)
    print(f'{src} to {dst}')
    shutil.copytree(src, dst)
    return len(os.listdir(dst))


def rename(dryrun: bool):
    """Renames all of the files to a simpler syntax %Y%m%d_%H%M%S_COUNT"""

    # Get the camera's DateTime of when the image was shot
    dst = os.path.join(os.path.expanduser('~'), "a6000Temp")
    dir_list = os.listdir(dst)
    file_renames = {}
    for file in dir_list:
        ti_m = os.path.getmtime(os.path.join(dst, file))

        # Converting the time in seconds to a timestamp to be stored on disk
        new_file_name = strftime('%Y%m%d_%H%M%S', localtime(ti_m))
        ext = os.path.splitext(file)[1]
        file_renames[file] = new_file_name + ext

    # Get counts of files that would be name the same name
    # DSLR cameras can take fast pictures so we want to ensure get them all
    value_counts = {}
    for value in file_renames.values():
        value_counts[value] = value_counts.get(value, 0) + 1

    unique_file_renames = {}
    for key, value in file_renames.items():
        count = value_counts[value]
        new_value = value

        # 1 is special since its was the the first picture taken
        if count != 1:
            split_filename = new_value.split('.')
            new_value = f"{split_filename[0]}_{count}.{split_filename[1]}"

        unique_file_renames[key] = new_value
        value_counts[value] -= 1

    for unique_file_rename in unique_file_renames:
        print(
            f"Move {unique_file_rename} to {unique_file_renames[unique_file_rename]}")
        if not dryrun:
            shutil.move(os.path.join(dst, unique_file_rename), os.path.join(
                dst, unique_file_renames[unique_file_rename]))


def move() -> None:
    """Moves all files from this temp directory to OneDrive where uploads can start"""
    src = os.path.join(os.path.expanduser('~'), "a6000Temp")

    # Camera Roll is still SkyDrive camera roll for some reason
    dst = os.path.join(os.path.expanduser(
        '~'), "OneDrive", "SkyDrive camera roll")
    dir_list = os.listdir(src)
    for file in dir_list:
        shutil.move(os.path.join(src, file), os.path.join(dst, file))
    shutil.rmtree(src)


if __name__ == '__main__':
    #  bug with video
    #  D:\MP_ROOT\100ANV01 handle moving these files as well... mp4
    if os.path.isdir(r'D:\DCIM'):
        src = os.path.join("D:", "\\", "DCIM", "100MSDCF")
        count = len(os.listdir(src))
        input(f"Found Disk. Files {count}. Press Enter to copy...")
        copied = copy(src)
        input(f"Copied {copied}. Press Enter to rename...")
        rename(False)
        input(f"Renamed {copied}. Press Enter to move...")
        move()
        print("Done. Delete all the images on camera to prevent duplications.")

