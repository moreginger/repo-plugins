import urllib,urllib2,re,os
import xbmcplugin,xbmcgui,xbmcaddon
from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup

__settings__ = xbmcaddon.Addon(id='plugin.video.engadget')
__language__ = __settings__.getLocalizedString
home = __settings__.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
nexticon = xbmc.translatePath( os.path.join( home, 'resources/next.png' ) )
videoq = __settings__.getSetting('video_quality')

def make_request(url, headers=None):
        try:
            if headers is None:
                headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                           'Referer' : 'http://www.engadget.com/'}
            req = urllib2.Request(url,None,headers)
            response = urllib2.urlopen(req)
            data = response.read()
            response.close()
            return data
        except urllib2.URLError, e:
            print 'We failed to open "%s".' % url
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            if hasattr(e, 'code'):
                print 'We failed with error code - %s.' % e.code
                xbmc.executebuiltin("XBMC.Notification(Engadget,HTTP ERROR: "+str(e.code)+",5000,"+icon+")")
                
                
def Categories():
        addDir(__language__(30000),'http://www.engadget.com/engadgetshow.xml',1,'http://www.blogcdn.com/www.engadget.com/media/2011/07/engadget-show-logo-1310764107.jpg')
        addDir(__language__(30001),'http://api.viddler.com/api/v2/viddler.videos.getByUser.xml?key=tg50w8nr11q8176liowh&user=engadget',2,icon)


def getEngadgetVideos(url):
        soup = BeautifulStoneSoup(make_request(url), convertEntities=BeautifulStoneSoup.XML_ENTITIES)
        videos = soup('video_list')[0]('video')
        page = int(soup('list_result')[0]('page')[0].string)+1
        for video in videos:
            name = video('title')[0].string
            link = video('html5_video_source')[0].string
            # link += '&ec_rate=406&ec_prebuf=10'
            link += '|User-Agent='
            link += urllib.quote_plus('Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1')
            thumb = video('thumbnail_url')[0].string
            length = video('length')[0].string
            addLink(name,link,length,thumb)
        addDir(__language__(30006),'http://api.viddler.com/api/v2/viddler.videos.getByUser.xml?key=tg50w8nr11q8176liowh&user=engadget&page='+str(page),2,nexticon)


def getEngadgetShow(url):
        url = 'http://www.engadget.com/engadgetshow.xml'
        soup = BeautifulStoneSoup(make_request(url), convertEntities=BeautifulStoneSoup.XML_ENTITIES)
        episodes = soup('item')
        for episode in episodes:
            try:
                url = episode('enclosure')[0]['url']
                title = episode('enclosure')[0]('itunes:subtitle')[0].string
                duration = episode('enclosure')[0]('itunes:duration')[0].string
                thumbnail = 'http://www.blogcdn.com/www.engadget.com/media/2011/07/engadget-show-logo-1310764107.jpg'
                if videoq == '0':
                        url=url.replace('900.mp4','500.mp4')
                elif videoq == '2':
                        url=url.replace('900.mp4','2500.mp4')
                else:
                        url=url
                addLink(title,url,duration,thumbnail,True)
            except:
                try:
                    Soup = BeautifulSoup(episode('description')[0].string, convertEntities=BeautifulSoup.HTML_ENTITIES)
                    thumb = Soup.img['src']
                    url = Soup('strong', text='Download the Show: ')[0].next['href']
                    title = episode.title.string
                    if videoq == '0':
                            url=url.replace('2500.mp4','700.mp4')
                    elif videoq == '1':
                            url=url.replace('2500.mp4','1100.mp4')
                    else:
                            url=url
                    addLink(title,url,'',thumb,True)
                except:
                    print "There was a problem adding the engadget show episode."


def DownloadFiles(url,filename):
        def download(url, dest):
            dialog = xbmcgui.DialogProgress()
            dialog.create(__language__(30001),__language__(30004), filename)
            urllib.urlretrieve(url, dest, lambda nb, bs, fs, url = url: _pbhook(nb, bs, fs, url, dialog))
        def _pbhook(numblocks, blocksize, filesize, url = None,dialog = None):
            try:
                percent = min((numblocks * blocksize * 100) / filesize, 100)
                dialog.update(percent)
            except:
                percent = 100
                dialog.update(percent)
            if dialog.iscanceled():
                dialog.close()
        # check for a download location, if not open settings
        if __settings__.getSetting('save_path') == '':
            __settings__.openSettings('save_path')
        filepath = xbmc.translatePath(os.path.join(__settings__.getSetting('save_path'),filename))
        download(url, filepath)
        if __settings__.getSetting('play') == "true":
            play=xbmc.Player().play( xbmc.translatePath( os.path.join( __settings__.getSetting('save_path'), filename ) ))


def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param


def addLink(name,url,duration,iconimage,showcontext=True):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Duration":duration } )
        if showcontext:
            try:
                filename = name.replace(':','-').replace(' ','_')+'.mp4'
            except:
                pass
            contextMenu = [(__language__(30004),'XBMC.Container.Update(%s?url=%s&mode=3&name=%s)' %(sys.argv[0],urllib.quote_plus(url),urllib.quote_plus(filename)))]
            liz.addContextMenuItems(contextMenu)
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

		
params=get_params()
url=None
name=None
mode=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if mode==None:
    print ""
    Categories()

if mode==1:
    print""
    getEngadgetShow(url)

if mode==2:
    print""
    getEngadgetVideos(url)

if mode==3:
    print""
    DownloadFiles(url,name)

xbmcplugin.endOfDirectory(int(sys.argv[1]))