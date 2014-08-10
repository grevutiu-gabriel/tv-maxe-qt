import os
import vlc
from PyQt5.QtCore import QObject, pyqtSignal

from tvmxutils import PLAYERSTATE_STOPPED, PLAYERSTATE_PLAYING
from tvmxutils import PLAYERSTATE_PAUSED


class VLCPlayer(QObject):
    stateChanged = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        QObject.__init__(self, *args, **kwargs)
        Instance = vlc.Instance()
        self.mp = vlc.MediaPlayer(Instance)
        self.evm = self.mp.event_manager()
        self.evm.event_attach(vlc.EventType.MediaPlayerStopped, self.callback, None)
        self.evm.event_attach(vlc.EventType.MediaPlayerPlaying, self.callback, None)
        self.evm.event_attach(vlc.EventType.MediaPlayerPaused, self.callback, None)
        self.evm.event_attach(
            vlc.EventType.MediaPlayerTimeChanged, self.force_volume, None)
        self.volume = 0

    def setMedia(self, url):
        self.mp.video_set_mouse_input(False)
        self.mp.video_set_key_input(False)
        self.mp.set_mrl(url)

    def play(self, xid):
        self.mp.set_xwindow(xid)
        self.mp.play()

    def pause(self):
        self.mp.pause()

    def unpause(self):
        self.mp.pause()

    def stop(self):
        self.mp.stop()

    def setVolume(self, value=None):
        self.volume = value
        self.mp.audio_set_volume(value)

    def setEq(self, b, c, s, h):
        try:
            b = (float(b) + float(100)) / float(100)
            c = (float(c) + float(100)) / float(100)
            s = (float(s) + float(100)) / float(100)
            h = (float(h) + float(100)) / float(100)
            self.mp.video_set_adjust_int(vlc.VideoAdjustOption.Enable, True)
            self.mp.video_set_adjust_float(vlc.VideoAdjustOption.Brightness, b)
            self.mp.video_set_adjust_float(vlc.VideoAdjustOption.Contrast, c)
            self.mp.video_set_adjust_float(vlc.VideoAdjustOption.Saturation, s)
            self.mp.video_set_adjust_float(vlc.VideoAdjustOption.Hue, h)
        except:
            pass

    def setRatio(self, ratio):
        if ratio == "Auto":
            ratio = None
        self.mp.video_set_aspect_ratio(ratio)

    def getTags(self):
        tags = ['', '']
        media = self.mp.get_media()
        title = media.get_meta(vlc.Meta.NowPlaying)
        artist = media.get_meta(vlc.Meta.Title)
        if artist:
            tags[0] = artist
        if title:
            tags[1] = title
        return tags

        def isPlaying(self):
            return self.mprunning

        def changeAudio(self, id):
            self.mp.audio_set_track(int(id))

    def state(self):
        state = self.mp.get_state()
        if state == vlc.State.NothingSpecial:
            return PLAYERSTATE_STOPPED
        if state == vlc.State.Stopped:
            return PLAYERSTATE_STOPPED
        if state == vlc.State.Ended:
            return PLAYERSTATE_STOPPED
        if state == vlc.State.Playing:
            return PLAYERSTATE_PLAYING
        if state == vlc.State.Buffering:
            return PLAYERSTATE_PLAYING
        if state == vlc.State.Opening:
            return PLAYERSTATE_PLAYING
        if state == vlc.State.Error:
            return PLAYERSTATE_STOPPED
        if state == vlc.State.Paused:
            return PLAYERSTATE_PAUSED
        return PLAYERSTATE_STOPPED

    @vlc.callbackmethod
    def callback(self, event, data):
        self.stateChanged.emit(self.state())

    @vlc.callbackmethod
    def force_volume(self, event, data):
        self.setVolume(self.volume)  # workaround

plugin_class = VLCPlayer
