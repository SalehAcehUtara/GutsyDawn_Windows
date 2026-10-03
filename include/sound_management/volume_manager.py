import wx

class VolumeManagerDialog(wx.Dialog):
    def __init__(self, parent, app_manager):
        super().__init__(parent, title="Volume Manager", size=(450, 460))
        self.app = app_manager
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # 1. Slider Volume Luar Game (Menu / Logo / BGM)
        lbl_luar = wx.StaticText(panel, label="Volume Luar Game (Musik Menu & Logo)")
        vbox.Add(lbl_luar, flag=wx.ALL, border=5)
        
        bgm_val = int(getattr(self.app.player, 'bgm_volume', 0.5) * 100)
        self.sl_luar = wx.Slider(panel, value=bgm_val, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.sl_luar.SetLineSize(1)
        self.sl_luar.SetPageSize(10)
        self.sl_luar.Bind(wx.EVT_SLIDER, self.on_luar_scroll)
        vbox.Add(self.sl_luar, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        
        # 2. Slider Volume Ambient (Lingkungan Game: awalan amb_)
        amb_val = int(getattr(self.app.player, 'ambient_volume', 1.0) * 100)
        lbl_amb = wx.StaticText(panel, label="Volume Ambient (Suara Lingkungan Game)")
        vbox.Add(lbl_amb, flag=wx.ALL, border=5)
        
        self.sl_amb = wx.Slider(panel, value=amb_val, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.sl_amb.SetLineSize(1)
        self.sl_amb.SetPageSize(10)
        self.sl_amb.Bind(wx.EVT_SLIDER, self.on_amb_scroll)
        vbox.Add(self.sl_amb, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        
        # 3. Slider Volume Media (Efek Suara Game & Chat: non-amb_)
        media_val = int(getattr(self.app.player, 'sfx_volume', 1.0) * 100)
        lbl_media = wx.StaticText(panel, label="Volume Media (Efek Suara & Notifikasi Chat)")
        vbox.Add(lbl_media, flag=wx.ALL, border=5)
        
        self.sl_media = wx.Slider(panel, value=media_val, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.sl_media.SetLineSize(1)
        self.sl_media.SetPageSize(10)
        self.sl_media.Bind(wx.EVT_SLIDER, self.on_media_scroll)
        vbox.Add(self.sl_media, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        
        # 4. Slider Volume Voice Chat (TeamTalk)
        voice_val = int(getattr(self.app.player, 'voice_volume', 1.0) * 100)
        lbl_voice = wx.StaticText(panel, label="Volume Voice Chat (TeamTalk)")
        vbox.Add(lbl_voice, flag=wx.ALL, border=5)
        
        self.sl_voice = wx.Slider(panel, value=voice_val, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
        self.sl_voice.SetLineSize(1)
        self.sl_voice.SetPageSize(10)
        self.sl_voice.Bind(wx.EVT_SLIDER, self.on_voice_scroll)
        vbox.Add(self.sl_voice, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=5)
        
        # Tombol Tutup Manager
        self.btn_close = wx.Button(panel, label="Tutup Manager")
        self.btn_close.Bind(wx.EVT_BUTTON, self.on_close)
        vbox.Add(self.btn_close, flag=wx.ALIGN_CENTER | wx.ALL, border=10)
        
        panel.SetSizer(vbox)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Centre()
        
        # Accessibility bindings (Focus & Keyboard)
        self.sl_luar.Bind(wx.EVT_KEY_DOWN, self.on_slider_key)
        self.sl_amb.Bind(wx.EVT_KEY_DOWN, self.on_slider_key)
        self.sl_media.Bind(wx.EVT_KEY_DOWN, self.on_slider_key)
        self.sl_voice.Bind(wx.EVT_KEY_DOWN, self.on_slider_key)
        
        self.sl_luar.Bind(wx.EVT_SET_FOCUS, self.on_focus_luar)
        self.sl_amb.Bind(wx.EVT_SET_FOCUS, self.on_focus_amb)
        self.sl_media.Bind(wx.EVT_SET_FOCUS, self.on_focus_media)
        self.sl_voice.Bind(wx.EVT_SET_FOCUS, self.on_focus_voice)
        self.btn_close.Bind(wx.EVT_SET_FOCUS, self.on_focus_close)
        
    def on_focus_luar(self, event):
        self.app.tts.speak(f"Volume Luar Game, {self.sl_luar.GetValue()} persen")
        event.Skip()
        
    def on_focus_amb(self, event):
        self.app.tts.speak(f"Volume Ambient, {self.sl_amb.GetValue()} persen")
        event.Skip()
        
    def on_focus_media(self, event):
        self.app.tts.speak(f"Volume Media, {self.sl_media.GetValue()} persen")
        event.Skip()
        
    def on_focus_voice(self, event):
        self.app.tts.speak(f"Volume Voice Chat, {self.sl_voice.GetValue()} persen")
        event.Skip()
        
    def on_focus_close(self, event):
        self.app.tts.speak("Tombol Tutup Manager")
        event.Skip()
        
    def on_luar_scroll(self, event):
        val = self.sl_luar.GetValue()
        self.app.player.bgm_volume = val / 100.0
        self.app.audio.update_bgm_volume(self.app.player.bgm_volume)
        
    def on_amb_scroll(self, event):
        val = self.sl_amb.GetValue()
        self.app.player.ambient_volume = val / 100.0
        if hasattr(self.app, 'ambience'):
            self.app.ambience.set_volume(self.app.player.ambient_volume)
            
    def on_media_scroll(self, event):
        val = self.sl_media.GetValue()
        self.app.player.sfx_volume = val / 100.0
        self.app.audio.update_sfx_volume(self.app.player.sfx_volume)

    def on_voice_scroll(self, event):
        val = self.sl_voice.GetValue()
        self.app.player.voice_volume = val / 100.0
        if hasattr(self.app, 'tt'):
            self.app.tt.set_voice_volume(val)
            
    def on_slider_key(self, event):
        keycode = event.GetKeyCode()
        obj = event.GetEventObject()
        val = obj.GetValue()
        
        if keycode in (wx.WXK_UP, wx.WXK_RIGHT, wx.WXK_DOWN, wx.WXK_LEFT, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN):
            if keycode in (wx.WXK_UP, wx.WXK_RIGHT):
                new_val = min(100, val + 1)
            elif keycode in (wx.WXK_DOWN, wx.WXK_LEFT):
                new_val = max(0, val - 1)
            elif keycode == wx.WXK_PAGEUP:
                new_val = min(100, val + 10)
            elif keycode == wx.WXK_PAGEDOWN:
                new_val = max(0, val - 10)

            obj.SetValue(new_val)
            self.app.tts.speak(f"{new_val} persen")
            
            # Update data player & audio secara manual karena SetValue tidak memicu event on_scroll
            if obj == self.sl_luar:
                self.app.player.bgm_volume = new_val / 100.0
                self.app.audio.update_bgm_volume(self.app.player.bgm_volume)
            elif obj == self.sl_amb:
                self.app.player.ambient_volume = new_val / 100.0
                if hasattr(self.app, 'ambience'):
                    self.app.ambience.set_volume(self.app.player.ambient_volume)
            elif obj == self.sl_media:
                self.app.player.sfx_volume = new_val / 100.0
                self.app.audio.update_sfx_volume(self.app.player.sfx_volume)
            elif obj == self.sl_voice:
                self.app.player.voice_volume = new_val / 100.0
                if hasattr(self.app, 'tt'):
                    self.app.tt.set_voice_volume(new_val)
                    
        elif keycode == wx.WXK_ESCAPE:
            self.on_close(event)
        elif keycode == wx.WXK_TAB:
            event.Skip()
        else:
            event.Skip()

    def on_close(self, event):
        self.app.player.save_profile()
        self.app.tts.speak("Volume manager ditutup.")
        self.EndModal(wx.ID_OK)
