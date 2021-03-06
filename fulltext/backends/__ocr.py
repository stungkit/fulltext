# sudo apt-get install tesseract-ocr
# sudo pip3 install pytesseract
# sudo apt-get install tesseract-ocr-[lang]

import errno

from PIL import Image

import pytesseract

from fulltext.util import assert_cmd_exists, MissingCommandException
from fulltext.util import BaseBackend


EXIF_ORIENTATION = 274  # cf ExifTags
EXIF_ROTATION = {
    3: 180,
    6: 270,
    8: 90
}


def read(img, **kargs):
    lang = kargs.get('lang', 'eng')
    rotate = kargs.get('rotate', None)

    im = Image.open(img)

    if rotate is None:
        try:
            exif = im._getexif()

        except AttributeError:
            # No EXIF data, no rotation necessary.
            pass

        else:
            if exif is not None:
                rotate = EXIF_ROTATION.get(exif.get(EXIF_ORIENTATION, None), 0)

    if rotate:
        im = im.rotate(rotate)

    try:
        return pytesseract.image_to_string(im, lang=lang)

    except IOError as e:
        if e.errno == errno.ENOENT:
            raise MissingCommandException('tesseract')
        raise


class Backend(BaseBackend):

    def check(self, title):
        assert_cmd_exists('tesseract')

    def handle_fobj(self, path_or_file):
        return read(path_or_file, **self.kwargs)

    handle_path = handle_fobj
