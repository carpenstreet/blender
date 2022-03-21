import configparser
import json
import logging
import os
import os.path
import platform
import shutil
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request
import webbrowser
from datetime import datetime
from distutils.dir_util import copy_tree
from distutils.version import StrictVersion

import requests
import json

config = configparser.ConfigParser()
cwdpath = os.path.dirname(os.path.abspath(__file__))

appversion = "1.9.8"
dir_ = ""
lastversion = ""
installedversion = ""
LOG_FORMAT = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(
    filename=cwdpath + "\\BlenderUpdater.log", format=LOG_FORMAT, level=logging.DEBUG, filemode="w"
)

logger = logging.getLogger()

if os.path.isfile(cwdpath + "\\config.ini"):
    config_exist = True
    logger.info("Reading existing configuration file")
    config.read(cwdpath + "\\config.ini")
    dir_ = config.get("main", "path")
    lastcheck = config.get("main", "lastcheck")
    lastversion = config.get("main", "lastdl")
    installedversion = config.get("main", "installed")
    flavor = config.get("main", "flavor")

url = "https://api.github.com/repos/acon3d/ABLER/releases/latest"
# Do path settings save here, in case user has manually edited it
config.read(cwdpath + "\\config.ini")
config.set("main", "path", dir_)
with open(cwdpath + "\\config.ini", "w") as f:
    config.write(f)
f.close()

req = ""
req = requests.get(url)
try:
    req = requests.get(url)
    print(req)
except Exception:
    logger.error("No connection to Blender nightly builds server")
info = {}
if req is not None:
    main_tag = req.json()['name'][1:]
    for asset in req.json()['assets']:
        if "Windows" in asset['browser_download_url'] and "zip" in asset['browser_download_url']:
            info["url"] = asset['browser_download_url']
            info["os"] = "Windows"
            info["filename"] = asset['browser_download_url'].split("/")[-1]
            info["version"] = main_tag
            info["arch"] = "x64"


    """Download routines."""

    url = info["url"]
    info_version = info["version"]
    variation = info["arch"]

    if StrictVersion(info_version) > StrictVersion(installedversion):
        if os.path.isdir(cwdpath + "\\blendertemp"):
            shutil.rmtree(cwdpath + "\\blendertemp")

        os.makedirs(cwdpath + "\\blendertemp")
        file = urllib.request.urlopen(url)
        totalsize = file.info()["Content-Length"]

        with open(cwdpath + "\\config.ini", "w") as f:
            config.write(f)
        f.close()

        ##########################
        # Do the actual download #
        ##########################

        config.read(cwdpath + "\\config.ini")
        config.set("main", "path", dir_)
        config.set("main", "flavor", variation)
        config.set("main", "installed", info_version)
        
        dir_ = os.path.join(dir_, "")
        filename = cwdpath + "\\blendertemp\\" + info["filename"]

        logger.info(f"Starting download thread for {url}, version {info_version}")

        urllib.request.urlretrieve(url, filename)
        shutil.unpack_archive(filename, cwdpath + "\\blendertemp\\")
        source = next(os.walk(cwdpath + "\\blendertemp\\"))[1]
        copy_tree(os.path.join(cwdpath + "\\blendertemp\\", source[0]), dir_)
        shutil.rmtree(cwdpath + "\\blendertemp")

        logger.info(f"Finished download thread for {url}, version {info_version}")
