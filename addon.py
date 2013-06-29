'''
Created on Apr 5, 2012

@author: Scott Brown
'''

import urllib
import os
import sys
import xbmc
import xbmcaddon
import xbmcgui

Addon = xbmcaddon.Addon()
__addon_path__ = Addon.getAddonInfo('path')
__scriptid__ = Addon.getAddonInfo('id')
__scriptname__ = Addon.getAddonInfo('name')
__cwd__ = Addon.getAddonInfo('path')
__version__ = Addon.getAddonInfo('version')

BASE_RESOURCE_PATH = xbmc.translatePath(os.path.join(__addon_path__, 'resources'))
sys.path.append(os.path.join(BASE_RESOURCE_PATH, "lib"))

from UIManager import UIManager
from EDLManager import EDLManager
from SRTMuteReplace import NewSRTCreator

import JSONUtils as data
import SubFinder as subf

# magic; id of this plugin's instance - cast to integer
_thisPlugin = int(sys.argv[1])

#create helper classes
ui = UIManager(_thisPlugin)

#setup loggers
subf.log = xbmc.log


def getInitialListing():
    """
    Creates a listing that XBMC can display as a directory
    listing
    @return list
    """
    listing = []
    listing.append(['Movies', sys.argv[0] + "?mode=movies"])
    listing.append(['TV Shows', sys.argv[0] + "?mode=tv"])
    return listing


def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


params = get_params()


def existsEDL(srtLoc):
    try:
        edlLoc = srtLoc[:-3] + "edl"
        return os.path.isfile(edlLoc)
    except:
        return False


def existsSRTbck(srtLoc):
    try:
        srtbck = srtLoc + ".bck"
        return os.path.isfile(srtbck)
    except:
        return False


def createEDL():
    try:
        filterLoc = os.path.join(BASE_RESOURCE_PATH, "filter.txt")
        safety = Addon.getSetting("safety")
        safety = float(safety) / 1000
        edl = EDLManager(srtLoc, filterLoc, safety)
        if existsEDL(srtLoc):
            ret = dialog.yesno(details['label'], Addon.getLocalizedString(30301))
            if not ret:
                return False
        edl.updateEDL()
        print Addon.getSetting('editsrt')
        if Addon.getSetting("editsrt") == "true":
            srt = NewSRTCreator(srtLoc, filterLoc)
            if existsSRTbck(srtLoc):
                os.rename(srtLoc + '.bck', srtLoc)
            if srt.createNewSRT():
                os.rename(srtLoc, srtLoc + '.bck')
                os.rename(srtLoc[:-3] + "tmp", srtLoc)
        return True
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return False


try:
    mode = urllib.unquote_plus(params["mode"])
except:
    mode = None

if mode == 'movie-details':
    movieid = urllib.unquote_plus(params["id"])
    xbmc.log("movieid: %s" % str(movieid))
    details = data.getMovieDetails(movieid)
    xbmc.log('details: %s' % details)

    dialog = xbmcgui.Dialog()
    ret = dialog.yesno(details['label'], Addon.getLocalizedString(30302))
    if not ret:
        sys.exit()

    fileLoc = details['file']
    finder = subf.SubFinder(Addon)
    srtLoc = finder.getSRT(fileLoc)
    if srtLoc:
        xbmc.log("Using srt file: %s" % srtLoc)
        if createEDL():
            dialog.ok(details['label'], Addon.getLocalizedString(30303))
        else:
            dialog.ok(details['label'], Addon.getLocalizedString(30307))
else:
    xbmc.log("Running %s v%s. Using default listing." % (__scriptid__, __version__))
    movieDict = data.GetAllMovies()
    xbmc.log("movieDict: %s" % movieDict)
    win = xbmcgui.WindowDialog()
    listing = []
    for movie in movieDict:
        url = sys.argv[0] + "?mode=movie-details&id=" + str(movie['movieid'])
        listing.append([movie['label'], movie['thumbnail'], url])
    ui.showThumbnailListing(listing)