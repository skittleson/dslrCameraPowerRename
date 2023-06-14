from libsonyapi.camera import Camera
from libsonyapi.actions import Actions
import PIL.Image
import requests
import PIL.ExifTags


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


def capture_and_download() -> str:
    camera = Camera()
    camera.do("setPostviewImageSize", ["Original"])
    response = None
    while response == None:
        response = camera.do(Actions.actTakePicture)
    return save_img_from_response(response['result'][0][0], 'img.jpg')


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
        except NoImageData as noimagedata:
            print("Last image processed had no data")
            running = False
        except:
            running = False
    print("Done")


if __name__ == '__main__':
    download_all()
