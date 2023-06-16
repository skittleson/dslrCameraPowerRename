import cv2
import os
import numpy as np
import imutils
import tempfile
import shutil


def align_images(image, template, maxFeatures=500, keepPercent=0.2, debug=False):
    """https://pyimagesearch.com/2020/08/31/image-alignment-and-registration-with-opencv/"""
    # convert both the input image and template to grayscale
    imageGray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    templateGray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    # use ORB to detect keypoints and extract (binary) local
    # invariant features
    orb = cv2.ORB_create(maxFeatures)
    (kpsA, descsA) = orb.detectAndCompute(imageGray, None)
    (kpsB, descsB) = orb.detectAndCompute(templateGray, None)
    # match the features
    method = cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
    matcher = cv2.DescriptorMatcher_create(method)
    matches = matcher.match(descsA, descsB, None)
    # sort the matches by their distance (the smaller the distance,
    # the "more similar" the features are)
    matches = sorted(matches, key=lambda x: x.distance)
    # keep only the top matches
    keep = int(len(matches) * keepPercent)
    matches = matches[:keep]
    # check to see if we should visualize the matched keypoints
    if debug:
        matchedVis = cv2.drawMatches(image, kpsA, template, kpsB,
                                     matches, None)
        matchedVis = imutils.resize(matchedVis, width=1000)
        cv2.imshow("Matched Keypoints", matchedVis)
        cv2.waitKey(0)

    # allocate memory for the keypoints (x, y)-coordinates from the
        # top matches -- we'll use these coordinates to compute our
        # homography matrix
    ptsA = np.zeros((len(matches), 2), dtype="float")
    ptsB = np.zeros((len(matches), 2), dtype="float")
    # loop over the top matches
    for (i, m) in enumerate(matches):
        # indicate that the two keypoints in the respective images
        # map to each other
        ptsA[i] = kpsA[m.queryIdx].pt
        ptsB[i] = kpsB[m.trainIdx].pt

    # compute the homography matrix between the two sets of matched
    # points
    (H, mask) = cv2.findHomography(ptsA, ptsB, method=cv2.RANSAC)
    # use the homography matrix to align the images
    (h, w) = template.shape[:2]
    aligned = cv2.warpPerspective(image, H, (w, h))
    # return the aligned image
    return aligned


def _blend_photos(img1_path: str, img2_path: str) -> str:
    """Given two image files, upscale 200%, align, then return a single image"""
    img1 = cv2.imread(img1_path)
    img2 = cv2.imread(img2_path)
    interpolation = cv2.INTER_CUBIC
    scale = 2
    upscaled1 = cv2.resize(
        img1, (img1.shape[1] * scale, img1.shape[0] * scale),	interpolation=interpolation)
    upscaled2 = cv2.resize(
        img2, (img2.shape[1] * scale, img2.shape[0] * scale),	interpolation=cv2.INTER_CUBIC)
    higher_resolution_img = align_images(upscaled1, upscaled2, debug=False)
    tmp = tempfile.NamedTemporaryFile(suffix='.JPG').name
    cv2.imwrite(tmp, higher_resolution_img)
    return tmp


def super_res(images: list[str]):
    """combine a list of images to one super high resolution image"""
    
    images_iter = iter(images)
    high_res_imgs = []
    for (img1, img2) in zip(images_iter, images_iter):
        print(f'combine {img1} {img2}')
        high_res_imgs.append(_blend_photos(img1, img2))
    
    if len(high_res_imgs) == 1:
        return high_res_imgs[0]
    else:
        return super_res(high_res_imgs)

class MustBeGeometricSequence(Exception):
    pass


if __name__ == '__main__':
    # cv2.imwrite(f'{os.curdir}/images/super_res.JPG', _blend_photos(
    #     f'{os.curdir}/images/img1.JPG', f'{os.curdir}/images/img2.JPG'))
    os.chdir(f'{os.curdir}/images')
    files = os.listdir(os.curdir)
    result = super_res(files)
    print(result)

