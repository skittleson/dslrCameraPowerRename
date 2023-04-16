import shutil
import wmi
import os
from time import strftime, localtime
import click
c = wmi.WMI()


def copy(device_id):
    """ Copy all files in camera directory to users directoy for human processing
    """
    # bug only works for Windows
    src = os.path.join(device_id, "\\", "DCIM", "100MSDCF")
    dst = os.path.join(os.path.expanduser('~'), "a6000Temp")
    print(f'{src} to {dst}')
    shutil.copytree(src, dst)


@click.group()
def cli():
    print("DSLR Camera File Helper/Mover")
    return


@cli.command()
def disks():
    """Returns a list of Device Ids and Volume Serial Numbers. Use Volume serial number for downloading command."""
    for disk in c.Win32_LogicalDisk():
        # if disk.Description == "Removable Disk":
            print(f"{disk.DeviceId} - {disk.VolumeSerialNumber}")


@cli.command()
@click.option('-s', '--serial', type=str, help='Serial number of disk', default="33326632")
def download(serial):
    """ When a disk with an the exact volume number is found, start transferring all the files to a temp location
    """
    for disk in c.Win32_LogicalDisk():
        if (disk.Description == "Removable Disk") and (disk.VolumeSerialNumber == str(serial)):
            print("Removal Camera Disk Found")
            print("Get some coffee, this can take a while...")
            copy(disk.DeviceId)
            print("Done Transferring")
            print("Review the images wanted. Follow up with rename command")


@cli.command()
@click.option('-d', '--dry-run', type=bool, help='Dry run', default=False)
def rename(dryrun):
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
            new_value = f"{value}_{count}"
        unique_file_renames[key] = new_value
        value_counts[value] -= 1

    for unique_file_rename in unique_file_renames:
        print(
            f"Move {unique_file_rename} to {unique_file_renames[unique_file_rename]}")
        if not dryrun:
            shutil.move(os.path.join(dst, unique_file_rename), os.path.join(
                dst, unique_file_renames[unique_file_rename]))


@cli.command()
def move():
    """Moves all files from this temp directory to OneDrive where uploads can start"""
    src = os.path.join(os.path.expanduser('~'), "a6000Temp")

    # Camera Roll is still SkyDrive camera roll for some reason
    dst = os.path.join(os.path.expanduser(
        '~'), "OneDrive", "SkyDrive camera roll")
    dir_list = os.listdir(src)
    for file in dir_list:
        shutil.move(os.path.join(src, file), os.path.join(dst, file))
    shutil.rmtree(src)

# download()
# rename()
# moveToOneDrive()


if __name__ == '__main__':
    cli()
