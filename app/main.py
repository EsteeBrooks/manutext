from flask import Flask, request, redirect, render_template, url_for
from flask.helpers import stream_with_context
from werkzeug.utils import secure_filename
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract
import os
import cv2
import numpy as np
from sklearn.metrics import accuracy_score

''' Set configurations:'''
app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = "app/static/img/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024

''' Function for getting the accuracy score and correct text for a file:'''
def get_accuracy_score(extracted_text, filename):
    # Collect all the correct text:
    with open("./app/data/text_data/" + filename[:-4] + ".txt", "r") as f:
        correct_text = f.read()

    correct_text_list = correct_text.split( )
    extracted_text_list = extracted_text.split()

    while len(correct_text_list) < len(extracted_text_list):
        correct_text_list += [""]
    
    while len(correct_text_list) > len(extracted_text_list):
        extracted_text_list += [""]
    
    score = accuracy_score(correct_text_list, extracted_text_list)
    return score, correct_text

''' Function for getting the predicted text using Tesseract '''
def ocr_core(filename):    
    img = Image.open(filename)
    text = pytesseract.image_to_string(img, lang='heb', config='--oem 1')
    return text

''' Function for checking the image is allowed '''
def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

'''Function for checking the image is an allowed size'''
def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False

''' Route for the about page '''
@app.route("/about")
def about():
    return render_template("about.html")


''' Route for home page (which is the upload image page):'''
@app.route("/", methods=["GET", "POST"])
@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        # If the image is not allowed, set as message:
        if not allowed_image_filesize(request.content_length):
            render_template('upload_image.html',
                            msg='Filesize exceeded maximum limit')

        image = request.files["image"]

        # If the image doesn't have a name, set as message:
        if image.filename == "":
            render_template('upload_image.html', msg='No filename')

        if allowed_image(image.filename):            
            # Save the image to static/img/uploads:
            filename = secure_filename(image.filename)
            image.save(os.path.join(
                app.config["IMAGE_UPLOADS"], filename))

            # call the OCR function on image:
            extracted_text = ocr_core(os.path.join(
                app.config["IMAGE_UPLOADS"], filename))

            # Get the accuracy score:
            score, correct_text= get_accuracy_score(extracted_text, filename)
            score = str(score)
            # Render template:
            src = url_for('static', filename=f"img/uploads/{filename}")
            return render_template('upload_image.html',
                                   msg='Successfully processed',
                                   extracted_text=extracted_text,
                                   correct_text=correct_text,
                                   img_src=src,
                                   score=score)
        else:
            # The file extension is not allowed so set that as the message:
            return render_template('upload_image.html', msg="That file extension is not allowed")
    # This is a GET method so just load the page with instructions as the message:
    return render_template("upload_image.html", msg='The extracted text will be displayed here')
