import os, os.path, subprocess, re
import textwrap

TYPE_MAP = {
    '.pdf':     '/usr/bin/pdftotext -q -nopgbrk {0} -',
    '.doc':     '/usr/bin/antiword {0}',
    '.docx':    '/usr/local/bin/docx2txt {0} -',  # http://sourceforge.net/projects/docx2txt/
    #'.xls':     '/usr/bin/xls2csv {0}',
    '.xls':     '/usr/bin/convertxls2csv -q -f {0} -c -',
    '.rtf':     '/usr/bin/unrtf --text --nopict {0}',
    '.odt':     '/usr/bin/odt2txt {0}',
    '.ods':     '/usr/bin/odt2txt {0}',
    '.zip':     '/usr/bin/zipinfo -2z {0}',
    '.tar.gz':  '/bin/tar tzf {0}',
    '.tar.bz2': '/bin/tar tjf {0}',
    '.rar':     '/usr/bin/unrar vb -p- -ierr -y {0}',
    '.htm':     '/usr/bin/html2text -nobs {0}',
    '.html':    '/usr/bin/html2text -nobs {0}',
    '.xml':     '/usr/bin/html2text -nobs {0}',
    '.jpg':     '/usr/bin/exiftool -s -s -s {0}',
    '.jpeg':    '/usr/bin/exiftool -s -s -s {0}',
    '.mpg':     '/usr/bin/exiftool -s -s -s {0}',
    '.mpeg':    '/usr/bin/exiftool -s -s -s {0}',
    '.mp3':     '/usr/bin/exiftool -s -s -s {0}',
    '.dll':     '/usr/bin/strings -n 18 {0}',
    '.exe':     '/usr/bin/strings -n 18 {0}',
}


class FullTextException(Exception):
    pass


# The idea of wrapping is to remove redundant whitespace and \r\n chars.
# We want to pack as much text as possible into as little space as possible.
# We also don't want to break up words or hyphenated phrases.
# We declare this here for efficiency reasons (we will use this over and over).
WRAPPER = textwrap.TextWrapper(
    width = 120,
    expand_tabs = False,
    replace_whitespace = True,
    drop_whitespace = True,
    break_long_words = False,
    break_on_hyphens = False,
)
STRIP_WHITE = re.compile(r'[ \t\v\f\r\n]+')


def get_type(filename):
    name, ext = os.path.splitext(filename)
    if ext in ('.gz', '.bz2') and name.endswith('.tar'):
        ext = '.tar' + ext
    if ext in TYPE_MAP:
        return ext


def get(filename, default=None, type=None):
    # TODO: allow an open file to be passed in, most of the tools
    # can accept data from stdin.
    if not os.path.exists(filename):
        if default is not None:
            return default
        raise FullTextException('File not found')
    if type is None:
        type = get_type(filename)
    try:
        cmd = TYPE_MAP[type]
    except KeyError:
        if default is not None:
            return default
        raise FullTextException('Unknown file type, known file types are: {0}'.format(' '.join(TYPE_MAP.keys())))
    cmd = cmd.format(filename)
    cmd = cmd.split()
    if not os.access(cmd[0], os.F_OK | os.X_OK):
        if default is not None:
            return default
        raise FullTextException('Cannot execute binary: {0}'.format(cmd[0]))
    try:
        text = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
    except:
        if default is not None:
            return default
        raise
    text = WRAPPER.fill(text.strip())
    # Remove adjacent whitespace
    text = STRIP_WHITE.sub(' ', text)
    return text


def main():
    for type, cmd in TYPE_MAP.items():
        cmd = cmd.split()
        if not os.access(cmd[0], os.F_OK | os.X_OK):
            print 'Cannot find converter for {0}, please install: {1}'.format(type, cmd[0])
    print 'All other converters present and accounted for.'

if __name__ == '__main__':
    main()