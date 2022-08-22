import sys, os, glob, getopt, time
import logging
from PIL import Image

# STATIC **********************************************************************

FILE_EXT = 'png'
NAME_LEN = 8
NAME_UPPER = True
PSD04_BOX_SIZE = (55, 62)
PSD04_BOX_SPACING_X = 59
PSD04_TEMPLATE = '04-template.png'
PSD04 = '04.png'

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
    for i in items:
        print(i.index)
        print(i.file)
        print(i.name)
        print(i.psd04thumb)
    items = psd04createstep(items, boxartdirpath)

# https://note.nkmk.me/en/python-pillow-paste/
def psd04createstep(items, boxartdirpath):
    file = os.path.join(boxartdirpath, PSD04)
    im1 = Image.open(os.path.join(boxartdirpath, PSD04_TEMPLATE))
    back_im = im1.copy()
    back_im = im1.convert('RGB')
    for i in items:
        im2 = Image.open(i.psd04thumb)
        box = (i.index * PSD04_BOX_SPACING_X, 0)
        back_im.paste(im2, box)
    back_im = back_im.convert('P')
    back_im.save(file, quality=95)
    return items

def filestep(items, path):
    items = []
    files = glob.glob(f"{path}/*.{FILE_EXT}")
    index = 0
    for file in files:
        print(file)
        if '04.png' in file:
            continue
        if '04-template.png' in file:
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
        i.psd04thumb = psd04thumb(i.file, i.name)
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
