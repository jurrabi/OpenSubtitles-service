# -*- coding: utf-8 -*- 

from core import *
import xbmc

def search_subtitles( item ):
  """ Searchs for subtitles and returns list of found subtitles.
  
  --> item: Its a dictionary containing all needed information about the media we are serching subtitles for (, look in script.subtitles.main/gui.py for detailed info).
            It includes, at least, the following keys filled on entry:
            'file_original_path':(str)  Complete path of media file (utf-8 encoded). Please be advise to decode or convert to local filesystem encoding if needed.
            'year':(str) Only for movies. Year of Release.
            'season':(str) Only for tv episodes. Season of the episode
            'episode':(str) Only for tv episodes. Eposode number within the season indicated by 'season'.
            'tvshow':(str) Only for tv episodes. Name of the TV Show
            'title':(str) Name of the movie or tv episode
            Other might be useful entries:
            'temp':(str) Indicates that subtitles will be stored in a temporary place (when video is streamed).
  On exit search_subtitles can add entries to the item dictionary (service dependant) so the might be found by download_subtitles
  """

ok = False
  hash_search = False
  if len(item['tvshow']) > 0:                                            # It's a TvShow episode
    OS_search_string = ("%s S%.2dE%.2d" % (item['tvshow'],
                                           int(item['season']),
                                           int(item['episode']),)
                                          ).replace(" ","+")      
  else:                                                                  #If it's not a TV show its a movie
    if str(item['year']) == "":
      item['title'], item['year'] = xbmc.getCleanMovieTitle( item['title'] )

    OS_search_string = item['title'].replace(" ","+")
    
  log( __name__ , "Search String [ %s ]" % (OS_search_string,))     
 
  if item['temp'] :                        #For streamed files we can't do a Hash Search
    hash_search = False
    file_size   = "000000000"
    SubHash     = "000000000000"
  else:                                    #else we calculate and store the hash info
    try:
      file_size, SubHash   = hashFile(item['file_original_path'])
      log( __name__ ,"xbmc module hash and size")
      hash_search = True
    except:  
      file_size   = ""
      SubHash     = ""
      hash_search = False
  
  if file_size != "" and SubHash != "":
    log( __name__ ,"File Size [%s]" % file_size )
    log( __name__ ,"File Hash [%s]" % SubHash)
  
  log( __name__ ,"Search by hash and name %s" % (os.path.basename( item['file_original_path'] ),))
  item['subtitles_list'], item['msg'] = OSDBServer().searchsubtitles( OS_search_string, item['3let_language'], hash_search, SubHash, file_size  )

# 2 below items need to be returned to main script
# item['subtitles_list'] list of all subtitles found, needs to include below items. see searchsubtitles above for more info
#                        "language_name"
#                        "filename"
#                        "rating"
#                        "language_flag"
# item['msg'] message notifying user of any errors

  return item

######## Standard Download function ###########
# as per search_subtitles explanation
#
# 3 below items are needed as a result
# item['zipped']   - is subtitle in zip?
# item['file']     - file where unzipped subtitle is saved ,
#                    main script will remame it and copy to 
#                    correct location(will be ignored if item['zipped'] is true
# item['language'] - language of the subtitle file. 
#                    it can be Full language name, 2 letter(ISO 639-1) or 3 letter(ISO 639-2)
#                    e.g English or en or eng
#                    e.g Serbian or sr or scc
###############################################
def download_subtitles (item):
  item['file'] = os.path.join(item['tmp_sub_dir'], "%s.srt" % item['subtitles_list'][item['pos']][ "ID" ])
  result = OSDBServer().download(item['subtitles_list'][item['pos']][ "ID" ], item['file'])
  if not result:
    import urllib
    log( __name__,"Download Using http://")
    urllib.urlretrieve(item['subtitles_list'][item['pos']][ "link" ],item['zip_subs'])  
  else:
    log( __name__,"Download Using XMLRPC")
  item['zipped'] = not result
  item['language'] = item['subtitles_list'][item['pos']][ "language_name" ]
  
  return item    
