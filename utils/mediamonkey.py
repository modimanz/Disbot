import win32com.client

boolReps = ['F', 'T']   # hacky!
quit = False
class MMEventHandlers():
    def __init__(self):
        self._play_events = 0

    def showMM(self):
        # note: MMEventHandlers instance includes all of SDBApplication members as well
        playing = self.Player.isPlaying
        paused = self.Player.isPaused
        isong = self.Player.CurrentSongIndex
        print('Play', boolReps[playing], '; Pause', boolReps[paused], '; iSong', isong)
        if playing:
            print('>>')
            self.Player.CurrentSong.Title[:40]
        else:
            print()

    def OnShutdown(self):   #OK
        global quit
        print('>>> SHUTDOWN >>> buh-bye')
        quit = True
    def OnPlay(self):       #OK
        self._play_events += 1
        print("PLAY #")
        self.showMM()
    def OnPause(self):      #OK
        print("PAUS #")
        self.showMM()

    def OnStop(self):
        print("STOP #")
        self.showMM()
    def OnTrackEnd(self):
        print("TRKE #")
        self.showMM()
    def OnPlaybackEnd(self):
        print("PLYE #")
        self.showMM()
    def OnCompletePlaybackEnd(self):
        print("LSTE #")
        self.showMM()
    def OnSeek(self):       #OK
        print("SEEK #")
        self.showMM()
    def OnNowPlayingModified(self):     #OK
        print("LIST #")
        self.showMM()

    # OnTrackSkipped gets an argument
    def OnTrackSkipped(self, track):  #OK (only when playing)
        print("SKIP #")
        self.showMM()
        # the type of any argument to an event is PyIDispatch
        # here, use PyIDispatch.Invoke() to query the 'Title' attribute for printing
        print('[%s]' % track.Invoke(3,0,2,True))

def search_and_play(query):
    # Create a MediaMonkey application object
    mm = win32com.client.DispatchWithEvents("SongsDB.SDBApplication", MMEventHandlers)

    # Get a reference to the MediaMonkey library
    library = mm.Library

    # Search for tracks matching the query
    tracks = library.Search(query)

    if tracks:
        # Play the first matching track
        track = tracks.Item(0)
        track.Play()
        print("Now playing: %s" % track.Title)
    else:
        print("No matching tracks found.")

# Example usage: search for tracks containing "love" in the title
search_query = "love"
search_and_play(search_query)