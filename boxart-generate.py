import sys, os, glob, getopt, time
import logging
from PIL import Image, ImageDraw, ImageFont

# STATIC **********************************************************************

FILE_EXT = 'png'
TMP_DIR = '_tmp'

PSD01 = '01.png'
PSD01_BOX_SPACING_X = 10
PSD01_BOX_SPACING_Y = 28
PSD01_BOX_SPACING_T = 154

NAME_LEN = 16
PSD01_NAME_SIZE = 22
PSD01_BOX_COLOR = (255,255,255)
PSD01_NAME_FONT = 'upheavtt.ttf'
PSD01_NAME_BORDER_COLOR = (96,96,96)
PSD01_NAME_BORDER_SIZE = 2

PSD03 = '03.png'
PSD03_BOX_SIZE = (82, 94)
PSD03_BOX_POS = (240, 0)
PSD03_BOX_BORDER = (80, 27)

PSD04 = '04.png'
PSD04_BOX_SIZE = (51, 58)
PSD04_BOX_POS = (59, 0)
PSD04_BOX_BORDER = (2, 2)

RES_DIR = 'resources'
RES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), RES_DIR)

# PUBLIC **********************************************************************

class Item:
  def __init__(self, file):
    self.file = file

class Box:
  def __init__(self, x, y, marginx, marginy):
    self.x = x
    self.y = y
    self.marginx = marginx
    self.marginy = marginy

# PRIVATE *********************************************************************

def process(boxartdirpath):
    items = []
    items = filestep(items, boxartdirpath)
    items = namestep(items)
    psd01 = psd01createstep(items, boxartdirpath)
    items = psd03thumbstep(items, boxartdirpath)
    psd03 = psd03createstep(items, boxartdirpath)
    items = psd04thumbstep(items, boxartdirpath)
    psd04 = psd04createstep(items, boxartdirpath)
    print('Batch Result:')
    print(psd01)
    print(psd03)
    print(psd04)

def psd01createstep(items, path):
    tmpdir = createdir(os.path.join(path, TMP_DIR, '01'))
    tmpfile = os.path.join(tmpdir, PSD01)
    file = os.path.join(path, PSD01)
    tpl = os.path.join(RES_PATH, PSD01)
    im1 = Image.open(tpl)
    back_im = im1.copy()
    back_im = back_im.convert('RGB')
    back_im.save(tmpfile, quality=95)
    for i in items:
        xy = ( PSD01_BOX_SPACING_X, PSD01_BOX_SPACING_T + i.index * PSD01_BOX_SPACING_Y)
        name = f'{i.index + 1}. {i.name}'
        writetexttoimage(tmpfile, name, xy)
    dirname = os.path.basename(os.path.normpath(path))
    title = f'{dirname.replace("_"," ")}'
    writetexttoimage(tmpfile, title, (30, 127))
    im2 = Image.open(tmpfile)
    im2 = im2.convert('P')
    im2.save(file, quality=95)
    return file

# https://note.nkmk.me/en/python-pillow-paste/
def psd04createstep(items, path):
    file = os.path.join(path, PSD04)
    tmpfile = pastthumbs(items, path, PSD04, '04', 'psd04thumb', PSD04_BOX_POS, PSD04_BOX_BORDER)
    file = saveto8bit(tmpfile, file)
    return file

def psd03createstep(items, path):
    file = os.path.join(path, PSD03)
    tmpfile = pastthumbs(items, path, PSD03, '03', 'psd03thumb', PSD03_BOX_POS, PSD03_BOX_BORDER)
    file = saveto8bit(tmpfile, file)
    return file

def pastthumbs(items, path, key, key2, fieldname, pos, border):
    tmpdir = createdir(os.path.join(path, TMP_DIR, key2))
    tmpfile = os.path.join(tmpdir, key)
    tplfile = os.path.join(RES_PATH, key)
    im1 = Image.open(tplfile)
    back_im = im1.copy()
    back_im = im1.convert('RGB')
    for i in items:
        im2 = Image.open(getattr(i, fieldname))
        box = (i.index * pos[0] + border[0], i.index * pos[1] + border[1])
        back_im.paste(im2, box)
    back_im.save(tmpfile, quality=95)
    return tmpfile

def saveto8bit(file, new):
    im1 = Image.open(file)
    back_im = im1.copy()
    back_im = back_im.convert('P')
    back_im.save(new, quality=95)
    return new 

def createthumbsbanner(items, file, tplbox, tplfile, tmpfile):
    im1 = Image.open(tplfile)
    back_im = im1.copy()
    back_im = im1.convert('RGB')
    for i in items:
        im2 = Image.open(i.psd04thumb)
        box = (i.index * tplbox.x + tplbox.marginx, tplbox.marginy)
        back_im.paste(im2, box)
    back_im.save(tmpfile, quality=95)
    back_im = back_im.convert('P')
    back_im.save(file, quality=95)

def filestep(items, path):
    items = []
    files = glob.glob(f"{path}/*.{FILE_EXT}")
    index = 0
    for file in files:
        print(file)
        if '04.png' in file:
            continue
        if '03.png' in file:
            continue
        if '01.png' in file:
            continue
        item = Item(file)
        item.index = index
        index = index + 1
        items.append(item)
    return items

def namestep(items):
    for i in items:
        i.name = buildname(i.file)
    return items

def psd04thumbstep(items, path):
    return createthumbs(items, path, '04', 'psd04thumb', PSD04_BOX_SIZE)

def psd03thumbstep(items, path):
    return createthumbs(items, path, '03', 'psd03thumb', PSD03_BOX_SIZE)

def createthumbs(items, path, key, attrname, box):
    tmpdir = createdir(os.path.join(path, TMP_DIR, key))
    for i in items:
        tmpfile = os.path.join(tmpdir, f'{i.index}.{FILE_EXT}')
        thumb = createthumb(i.file, tmpfile, box)
        setattr(i, attrname, thumb)
    return items

def createthumb(file, tmpfile, size):
    rgbimg = Image.open(file)
    resizeimg = rgbimg.resize(size)
    resizeimg = resizeimg.convert('RGB')
    resizeimg.save(tmpfile)
    return tmpfile

def createdir(tmpname):
    isExist = os.path.exists(tmpname)
    if not isExist:
        os.makedirs(tmpname)
    return tmpname

def buildname(path):
    filename = os.path.basename(path)
    name = os.path.splitext(filename)[0]
    case = name.upper()
    trunc = case[:NAME_LEN]
    return trunc

def writetexttoimage(file, text, xy):
    img = Image.open(file)
    d1 = ImageDraw.Draw(img)
    font = getfont(PSD01_NAME_FONT, PSD01_NAME_SIZE)
    thick = PSD01_NAME_BORDER_SIZE
    x = xy[0]
    y = xy[1]
    shadowcolor = PSD01_NAME_BORDER_COLOR
    d1.text((x-thick, y), text, font=font, fill=shadowcolor)
    d1.text((x+thick, y), text, font=font, fill=shadowcolor)
    d1.text((x, y-thick), text, font=font, fill=shadowcolor)
    d1.text((x, y+thick), text, font=font, fill=shadowcolor)
    d1.text(xy, text, PSD01_BOX_COLOR, font=font)
    img.save(file)

def getfont(fontname, fontsize):
    fonts_path = os.path.join(RES_PATH, fontname)
    font = ImageFont.truetype(fonts_path, fontsize)
    return font

# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
def getargs(argv, configs, helpmsg=None):
    """getargs(argv, configs, helpmsg)
    
    Return dictionnary with long opt names as keys and arg as values. 
    From Reading command line arguments, using short or long opt names with default values from configs object.

    Parameters
    ----------
    argv
        |sys.argv[1:]|
    configs
        |array<dictionnary['opt':str,'shortopt':str,'longopt':str,'defarg':str]>|
        example : [{'opt':'myopt'},...] or [{'shortopt':'mo','longopt':'myopt','defarg':'False'},...]
    helpmsg
        |str(optionnal)|
        example : 'python myscript.py -m <myopt>'

    Returns
    -------
    dictionnary[key(longopt):str(arg or defarg)]

    Usage
    -----
    argv = sys.argv[1:]

    helpmsg = 'python myscript.py -m <myopt>'

    configs = [{ 'opt':'myopt', 'defarg':'False' } ]

    argdic = getargs(argv, configs, helpmsg)

    myoptarg = argdic.get('myopt')
    """
    shortopts = "h"
    longopts = []
    defhelpmsg = 'Usage: python [script].py'
    for conf in configs:
        # DEF VALS
        if not 'longopt' in conf.keys():
            conf['longopt'] = conf['opt']
        if not 'shortopt' in conf.keys():
            conf['shortopt'] = conf['longopt'][0]
        if not 'defarg' in conf.keys():
            conf['defarg'] = None
        # BUILD PARAMS
        shortopts += f"{conf['shortopt']}:"
        longopts.append(f"{conf['longopt']}=")
        defhelpmsg += f" --{conf['longopt']} <{conf['defarg']}>"
    help = defhelpmsg if helpmsg is None else helpmsg
    # READ OPT
    try:
        opts, args = getopt.getopt(argv,shortopts,longopts)
    except getopt.GetoptError:
        print(help)
        sys.exit(2)
    # GET ARGS
    res = {}
    for opt, arg in opts:
        if opt == '-h':
            print(help)
            sys.exit()
        else:
            for conf in configs:
                if opt in (f"-{conf['shortopt']}", f"--{conf['longopt']}"):
                    res[conf['longopt']] = arg
                    continue
    # DEFAULT ARGS
    print("Running default command line with: ")
    for conf in configs:
        if not conf['longopt'] in res.keys():
            res[conf['longopt']] = conf['defarg']
        print(f"argument --{conf['longopt']}: '{res[conf['longopt']]}'")
    return res

# DEPRECATED from distutils.util import strtobool
# 'For these functions, and any others not mentioned here, you will need to reimplement the functionality yourself'
def strtobool (val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = val.lower()
    if val in ('y', 'yes', 't', 'true', 'on', '1'):
        return 1
    elif val in ('n', 'no', 'f', 'false', 'off', '0'):
        return 0
    else:
        raise ValueError("invalid truth value %r" % (val,))

# SCRIPT **********************************************************************

def main(argv):
    argd = getargs(argv, [
        { 'opt':'dirpath',  'defarg':'.' }])
    dirpath = argd.get("dirpath")
    print("GGM boxart generator")
    print(f'Exec. path : {os.getcwd()}')
    print(f'BoxArt. path : {dirpath}')
    process(dirpath)

if __name__ == "__main__":
    main(sys.argv[1:])
