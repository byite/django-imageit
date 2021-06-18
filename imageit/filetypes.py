import filetype


class svgType(filetype.Type):
    """
    Implements a mime type matcher for svg files
    """
    MIME = 'image/svg+xml'
    EXTENSION = 'svg'

    def __init__(self):
        super(svgType, self).__init__(
            mime=svgType.MIME,
            extension=svgType.EXTENSION
        )

    def match(self, buf):
        str_buf = str(buf)
        location = str_buf.lower().find('<svg')
        return location >= 0