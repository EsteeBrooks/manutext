from flask import Flask, request, redirect, render_template
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

app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = "/Users/esteebrooks/Documents/Machine_Learning/final_project/manutext2/manutext/app/static/img"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 0.5 * 1024 * 1024


def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    image = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    # img = Image.open(filename)
    # Rescale the image:
    # img = cv2.resize(img, None, fx=1.2, fy=1.2, interpolation=cv2.INTER_CUBIC)
    # # Convert image to grayscale:
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # # Applying dilation and erosion to remove the noise
    # kernel = np.ones((1, 1), np.uint8)
    # img = cv2.dilate(img, kernel, iterations=1)
    # img = cv2.erode(img, kernel, iterations=1)

    # # Apply blur:
    # cv2.threshold(cv2.medianBlur(img, 3), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.medianBlur(image,5)
    # cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    kernel = np.ones((5,5),np.uint8)
    image = cv2.dilate(image, kernel, iterations = 1)
    
    kernel = np.ones((5,5),np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

    image = cv2.Canny(image, 100, 200)

    # Get a searchable PDF
    pdf = pytesseract.image_to_pdf_or_hocr(image, extension='pdf', lang='heb', config='--oem 1')
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path+"/test.pdf", 'w+b') as f:
        f.write(pdf) # pdf type is bytes by default

    # coords = np.column_stack(np.where(image > 0))
    # angle = cv2.minAreaRect(coords)[-1]
    # if angle < -45:
    #     angle = -(90 + angle)
    # else:
    #     angle = -angle
    # (h, w) = image.shape[:2]
    # center = (w // 2, h // 2)
    # M = cv2.getRotationMatrix2D(center, angle, 1.0)
    # img = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    text = pytesseract.image_to_string(image, lang='heb', config='--oem 1')
    return text


def allowed_image(filename):

    if not "." in filename:
        return False

    ext = filename.rsplit(".", 1)[1]

    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False


def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/", methods=["GET", "POST"])
@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    print(request.method)
    if request.method == "POST":
        if not allowed_image_filesize(request.content_length):
            render_template('upload_image.html',
                                msg='Filesize exceeded maximum limit')
        image = request.files["image"]
        if image.filename == "":
                render_template('upload_image.html', msg='No filename')

        if allowed_image(image.filename):
            dir_path = os.path.dirname(os.path.realpath(__file__))
            # Save the image to static/img/uploads:
            filename = secure_filename(image.filename)
            image.save(dir_path + "/img/uploads/" + filename)

            # call the OCR function on image:
            extracted_text = ocr_core(os.path.join(
            app.config["IMAGE_UPLOADS"], filename))
            src = filename
            print(src)
            # src = os.path.join(app.config["IMAGE_UPLOADS"], filename)
            # src = os.listdir(app.config["IMAGE_UPLOADS"])
            return render_template('upload_image.html',
                                       msg='Successfully processed',
                                       extracted_text=extracted_text,
                                       img_src=src)

        else:
            return render_template('upload_image.html', msg="That file extension is not allowed")

    return render_template("upload_image.html", msg='The extracted text will be displayed here')
