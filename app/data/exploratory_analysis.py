import os
import re
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import os
import cv2
import numpy as np
from sklearn.metrics import accuracy_score
import pandas as pd
from matplotlib import pyplot as plt

''' The purpose of this file is to look at the performace of the model overall.
It is see if  the accuracy score overall is consistantly bad overall or does better
some images and worse on others.  '''

# Get the accuracy score and correct text:
def get_accuracy_score(extracted_text, filename):
    # Collect all the correct text:
    with open("./text_data/" + filename[:-4] + ".txt", "r") as f:
        correct_text = f.read()

    correct_text_list = correct_text.split( )
    extracted_text_list = extracted_text.split()

    while len(correct_text_list) < len(extracted_text_list):
        correct_text_list += [""]
    
    while len(correct_text_list) > len(extracted_text_list):
        extracted_text_list += [""]
    
    score = accuracy_score(correct_text_list, extracted_text_list)
    return score, correct_text

# Get the predicted text: 
def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    
    img = Image.open(filename)
    text = pytesseract.image_to_string(img, lang='heb', config='--oem 1')
    return text

all_score = []
# Loop through each image and add accuracy to list:
# CHANGE THIS TO CORRRECT PATH:
directories = ['./BiblIA_dataset/Sephardi/',
               './BiblIA_dataset/Ashkenazy/',
               './BiblIA_dataset/Italian/']

for directory in directories:
    # iterate over files in that directory
    for filename in os.listdir(directory):
        
        # Skipp .jpg files:
        if re.match('.*?(\.xml)', filename):
            continue
        

        f = os.path.join(directory, filename)

        # checking if it is a file
        if os.path.isfile(f):
            predicted_text = ocr_core(f)
            score, correct_text = get_accuracy_score(predicted_text, filename)
            all_score += [score]

# Print average and plot the histogram
print("Average accuracy score:", sum(all_score)/len(all_score))
plt.hist(all_score, 10)
plt.show()

'''' Output:Average accuracy score: 0.0008799837437847445. See google drive for histogram image'''

