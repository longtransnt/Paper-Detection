# -*- coding: utf-8 -*-
"""
Created on Wed Apr 13 20:45:22 2022

@author: ASUS
"""

import cv2
import numpy as np
from pathlib import Path
from skimage.filters import threshold_sauvola
import os


def applyPreprocesscingStep(image_name, output_dir):
    # =============================================================================
    #  Create output directory
    # =============================================================================
    im = cv2.imread(image_name, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # =============================================================================
    # create a CLAHE object (Arguments are optional).
    # =============================================================================
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    clahe_image = clahe.apply(gray)

    # =============================================================================
    # Sauvola Thresholding
    # =============================================================================
    window_size = 25
    thresh_sauvola = threshold_sauvola(clahe_image, window_size=window_size)
    binary_sauvola = clahe_image > thresh_sauvola
    sauvola_image = np.uint8(binary_sauvola * 255)

    # =============================================================================
    # INVERSE thresholding
    # =============================================================================
    th, sauvola_bin_image = cv2.threshold(
        sauvola_image, 0, 255, cv2.THRESH_BINARY_INV)

    size = 22
    img_denoised = remove_small_objects(sauvola_bin_image, size)
    img_denoised = img_denoised
    path, file_name = os.path.split(image_name)
    file_name, suffix = os.path.splitext(file_name)
    image_name = output_dir + "/" + file_name + "_pp.jpg"
    cv2.imwrite(image_name, img_denoised)
    return img_denoised, image_name

# =============================================================================
# Denoise
# =============================================================================


def remove_small_objects(img, min_size):
    # find all your connected components (white blobs in your image)
    connectivity = 8
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(
        img, connectivity, cv2.CV_32S)
    # connectedComponentswithStats yields every seperated component with information on each of them, such as size
    # the following part is just taking out the background which is also considered a component, but most of the time we don't want that.
    sizes = stats[1:, -1]
    nb_components = nb_components - 1

    img2 = img
    # for every component in the image, you keep it only if it's above min_size
    for i in range(0, nb_components):
        if sizes[i] < min_size:
            img2[output == i + 1] = 0

    return 255-img2
    # res = cv2.bitwise_not(img2)
    # return res
