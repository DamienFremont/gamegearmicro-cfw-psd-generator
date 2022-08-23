import sys, os, glob, getopt, time
import logging
from PIL import Image, ImageDraw, ImageFont

# STATIC **********************************************************************

FILE_EXT = 'png'
NAME_LEN = 16
NAME_UPPER = True
PSD04_BOX_SIZE = (55, 62)
PSD04_BOX_SPACING_X = 59
PSD04 = '04.png'
PSD01 = '01.png'
PSD01_BOX_SPACING_X = 30
PSD01_BOX_SPACING_Y = 28
PSD01_BOX_SPACING_T = 154
PSD01_BOX_COLOR = (255,255,255)
PSD01_NAME_FONT = 'upheavtt.ttf'
PSD01_NAME_SIZE = 22
PSD01_NAME_BORDER_COLOR = (96,96,96)
PSD01_NAME_BORDER_SIZE = 2

RES_DIR = 'resources'

RES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), RES_DIR)

# PUBLIC **********************************************************************

class Item:
  def __init__(self, file):
    self.file = file

# PRIVATE *********************************************************************

def process(boxartdirpath, templatedirpath):
    items = []
    items = filestep(items, boxartdirpath)
    items = namestep(items)
    items = psd04thumbstep(items)
    psd04 = psd04createstep(items, boxartdirpath)
    psd01 = psd01createstep(items, boxartdirpath)
    print('Batch Result:')
    print(psd04)
    print(psd01)

def psd01createstep(items, boxartdirpath):
    file = os.path.join(boxartdirpath, PSD01)
    tpl = os.path.join(RES_PATH, PSD01)
    im1 = Image.open(tpl)
    back_im = im1.copy()
    back_im = back_im.convert('RGB')
    back_im.save(file, quality=95)
    for i in items:
        xy = ( PSD01_BOX_SPACING_X, PSD01_BOX_SPACING_T + i.index * PSD01_BOX_SPACING_Y)
        writetexttoimage(file, i.name, xy)
    im2 = Image.open(file)
    im2 = im2.convert('P')
    im2.save(file, quality=95)
    return file

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
    print(fonts_path)
    font = ImageFont.truetype(fonts_path, fontsize)
    return font

# https://note.nkmk.me/en/python-pillow-paste/
def psd04createstep(items, boxartdirpath):
    file = os.path.join(boxartdirpath, PSD04)
    tpl = os.path.join(RES_PATH, PSD04)
    im1 = Image.open(tpl)
    back_im = im1.copy()
    back_im = im1.convert('RGB')
    for i in items:
        im2 = Image.open(i.psd04thumb)
        box = (i.index * PSD04_BOX_SPACING_X, 0)
        back_im.paste(im2, box)
    back_im = back_im.convert('P')
    back_im.save(file, quality=95)
    return file

def filestep(items, path):
    items = []
    files = glob.glob(f"{path}/*.{FILE_EXT}")
    index = 0
    for file in files:
        print(file)
        if '04.png' in file:
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

def psd04thumbstep(items):
    for i in items:
        i.psd04thumb = psd04thumb(i.file, i.index)
    return items

def psd04thumb(path, name):
    rgbimg = Image.open(path)
    resizeimg = rgbimg.resize(PSD04_BOX_SIZE)
    resizeimg = resizeimg.convert('RGB')
    dirname = os.path.dirname(path)
    tmpname = createdir(os.path.join(dirname, '_tmp', 'psd04thumbs'))
    mewfilename = os.path.join(tmpname, f'{name}.{FILE_EXT}')
    resizeimg.save(mewfilename)
    return mewfilename

def createdir(tmpname):
    isExist = os.path.exists(tmpname)
    if not isExist:
        os.makedirs(tmpname)
    return tmpname

def buildname(path):
    filename = os.path.basename(path)
    name = os.path.splitext(filename)[0]
    case = name.upper() if NAME_UPPER else name
    trunc = case[:NAME_LEN]
    return trunc

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
    print("GGM boxart generator")
    print(f'Exec. path : {os.getcwd()}')
    dirpath = argd.get("dirpath")
    print(f'BoxArt. path : {dirpath}')
    process(dirpath, 0)

if __name__ == "__main__":
    main(sys.argv[1:])
