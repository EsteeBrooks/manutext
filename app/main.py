from flask import Flask, render_template, request, redirect
import os
from flask.helpers import stream_with_context
from werkzeug.utils import secure_filename
try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract

app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = "/Users/esteebrooks/Documents/Machine_Learning/final_project/manutext2/manutext/app/static/img"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config["MAX_IMAGE_FILESIZE"] = 10 * 1024 * 1024  # 10MB


def ocr_core(filename):
    """
    This function will handle the core OCR processing of images.
    """
    text = pytesseract.image_to_string(Image.open(
        filename), lang='heb', config='--oem 1')
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


@app.route("/", methods=["GET", "POST"])
@app.route("/upload-image", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":

        if request.files:
            if "filesize" in request.cookies:
                if not allowed_image_filesize(request.cookies["filesize"]):
                    render_template('upload_image.html',
                                    msg='Filesize exceeded maximum limit')

                image = request.files["image"]

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

                    src = os.path.join(app.config["IMAGE_UPLOADS"], filename)
                    #src = "file:/" + src
                    print(src)
                    return render_template('upload_image.html',
                                           msg='Successfully processed',
                                           extracted_text=extracted_text,
                                           img_src=src)

                else:
                    return render_template('upload_image.html', msg="That file extension is not allowed")

    return render_template("upload_image.html", msg='The extracted text will be displayed here')
