from libsonyapi.camera import Camera
from libsonyapi.actions import Actions
import PIL.Image
import requests
import PIL.ExifTags
import cv2
import numpy as np
import time


def events():
    camera = Camera()  # create camera instance
    camera_info = camera.info()  # get camera camera_info
    print(camera_info)
    # print(camera.do("getAvailablePostviewImageSize"))
    print(camera.do("setPostviewImageSize", ["Original"]))


def analyze_pix():
    camera = Camera()  # create camera instance
    camera_info = camera.info()  # get camera camera_info
    print(camera_info)
    print(camera.services)
    print(camera.name)  # print name of camera
    print(camera.api_version)  # print api version of camera
    camera.do("setPostviewImageSize", ["Original"])
    response = camera.do(Actions.actTakePicture)  # take a picture
    print(response)
    image_uri = response['result'][0][0]
    print(image_uri)
    img_data = requests.get(image_uri).content
    with open('img.jpg', 'wb') as handler:
        handler.write(img_data)

    img = PIL.Image.open('img.jpg')
    tags(tags)


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


def super_resolution_basic():
    # https://github.com/Rudgas/Superresolution
    capture_and_download("img1.jpg")
    capture_and_download("img2.jpg")
    capture_and_download("img3.jpg")
    capture_and_download("img4.jpg")
    img1 = cv2.imread("img1.jpg")
    img2 = cv2.imread("img2.jpg")
    img3 = cv2.imread("img3.jpg")
    img4 = cv2.imread("img4.jpg")


    start = time.time()
    upscaled1 = cv2.resize(
        img1, (img1.shape[1] * 4, img1.shape[0] * 4),	interpolation=cv2.INTER_CUBIC)
    upscaled2 = cv2.resize(
        img2, (img2.shape[1] * 4, img2.shape[0] * 4),	interpolation=cv2.INTER_CUBIC)
    upscaled3 = cv2.resize(
        img3, (img3.shape[1] * 4, img3.shape[0] * 4),	interpolation=cv2.INTER_CUBIC)
    upscaled4 = cv2.resize(
        img4, (img4.shape[1] * 4, img4.shape[0] * 4),	interpolation=cv2.INTER_CUBIC)
    end = time.time()
    print(f"[INFO] bicubic resolution took {end - start:.6f} seconds")

    combined_image1 = cv2.addWeighted(upscaled1, 0.5, upscaled2, 0.5, 0)
    combined_image2 = cv2.addWeighted(upscaled3, 0.5, upscaled4, 0.5, 0)
    combined_image3 = cv2.addWeighted(combined_image1, 0.5, combined_image2, 0.5, 0)
    cv2.imwrite("superres.jpg", combined_image3)

    # cv2.imshow('Blended Image', blended_image)
    # cv2.waitKey(0)


def alpha_blend(image1, image2, alpha):
    return cv2.addWeighted(image1, alpha, image2, 1 - alpha, 0)


if __name__ == '__main__':
    super_resolution_basic()
