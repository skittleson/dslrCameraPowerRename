from libsonyapi.camera import Camera
from libsonyapi.actions import Actions
import PIL.Image
import requests
import PIL.ExifTags
import time
from image_utils import super_resolution_by_directory
import os


def analyze_pix():
    camera = Camera()  # create camera instance
    camera_info = camera.info()  # get camera camera_info
    print(camera_info)
    print(camera.services)
    print(camera.name)  # print name of camera
    print(camera.api_version)  # print api version of camera
    print(camera.do("getAvailableFocusMode"))
    camera.do(Actions.setFocusMode, "MF")
    camera.do("setPostviewImageSize", ["Original"])
    time.sleep(1)
    start = time.time()
    camera.do(Actions.actTakePicture)
    camera.do(Actions.actTakePicture)
    camera.do(Actions.actTakePicture)
    camera.do(Actions.actTakePicture)
    end = time.time()
    print(f"[INFO] 4 photos took {end - start:.6f} seconds")

    # response = camera.do(Actions.actTakePicture)  # take a picture
    # print(response)
    # image_uri = response['result'][0][0]
    # print(image_uri)
    # img_data = requests.get(image_uri).content
    # with open('img.jpg', 'wb') as handler:
    #     handler.write(img_data)

    # img = PIL.Image.open('img.jpg')
    # tags(tags)


def tags(img):
    exif = {
        PIL.ExifTags.TAGS[k]: v
        for k, v in img._getexif().items()
        if k in PIL.ExifTags.TAGS
    }
    print(exif)


def capture_and_download(filename="img.jpg") -> str:
    camera = Camera()
    camera.do("setPostviewImageSize", ["Original"])
    response = None
    while response == None:
        response = camera.do(Actions.actTakePicture)
    return save_img_from_response(response['result'][0][0], filename)


def capture(camera: Camera) -> str:
    camera = Camera()
    response = None
    while response == None:
        response = camera.do(Actions.actTakePicture)
    return response['result'][0][0]


def download_image(image_uri: str, filename: str) -> None:
    img_data = requests.get(image_uri).content
    print(len(img_data))
    if len(img_data) <= 0:
        raise NoImageData()
    with open(filename, 'wb') as handler:
        handler.write(img_data)


def save_img_from_response(image_uri: str, filename: str) -> str:
    img_data = requests.get(image_uri).content
    print(len(img_data))
    if len(img_data) <= 0:
        raise NoImageData()
    with open(filename, 'wb') as handler:
        handler.write(img_data)
    return image_uri


class NoImageData(Exception):
    pass


def download_all():
    img_uri = capture_and_download()
    image_index = int(img_uri[::-1].split('/')
                      [0].split('.')[1][::-1].split('DSC')[1])
    print(image_index)
    running = True
    while running:
        try:
            print(f'Downloading {str(image_index)}.jpg')
            save_img_from_response(img_uri, f'{str(image_index)}.jpg')
            new_image_index = image_index - 1
            img_uri = img_uri.replace(
                f'{str(image_index)}.JPG', f'{str(new_image_index)}.JPG',)
            image_index = new_image_index
        except NoImageData:
            print("Last image processed had no data")
            running = False
        except:
            running = False
    print("Done")


def super_resolution():
    """Take a series of 4 pictures then create one high resolution image from it"""

    camera = Camera()  # create camera instance
    camera_info = camera.info()  # get camera camera_info

    # Save a second while taking the photos
    camera.do(Actions.setFocusMode, "MF")
    camera.do("setPostviewImageSize", ["Original"])  # Only the original photo
    camera_photos = []
    start = time.time()
    for photo_iterator in range(1, 4):
        camera_photos.append(capture(camera))
    end = time.time()
    print(f"[INFO] taking pixs took {end - start:.6f} seconds")
    start = time.time()

    # save files to temp location
    tmp_iterator = 1
    local_photos = []
    for photo in camera_photos:
        # imutils.url_to_image
        path = f"{tmp_iterator}.JPG"
        download_image(photo, path)
        local_photos.append(path)
        tmp_iterator += 1
    end = time.time()
    print(f"[INFO] downloading pixs took {end - start:.6f} seconds")
    super = super_resolution_by_directory(f'{os.curdir}/images')
    print(super)


if __name__ == '__main__':
    super_resolution()
