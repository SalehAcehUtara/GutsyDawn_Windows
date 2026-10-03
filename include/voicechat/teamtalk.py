import threading

import asyncio

import sys

import os
import sys

import traceback

import platform



if platform.system() == 'Windows':
    if getattr(sys, 'frozen', False):
        try:
            os.add_dll_directory(os.path.join(os.path.dirname(sys.executable), 'dll'))
        except FileNotFoundError:
            pass
    else:
        try:
            os.add_dll_directory(os.path.join(sys._MEIPASS if getattr(sys, 'frozen', False) else os.getcwd(), 'dll'))
        except FileNotFoundError:
            pass



try:
    import pytalk
    HAS_PYTALK = True
except Exception as e:
    HAS_PYTALK = False
    PYTALK_ERROR = str(e)



class TeamTalkManager:

    def __init__(self, manager):

        self.manager = manager

        self.bot = None

        self.tt_instance = None

        self.mic_active = False

        self.connected = False

        self._thread = None

        self._loop = None

        self.is_running = False



    def start(self, nickname="Player"):

        if not HAS_PYTALK:
            self.manager.tts.speak(f"Modul pytalk gagal dimuat: {PYTALK_ERROR}")
            return



        if self.is_running:

            return

            

        self.manager.tts.speak("Menghubungkan ke Voice Chat TeamTalk...")



        self.is_running = True

        self._thread = threading.Thread(target=self._run_async_loop, args=(nickname,), daemon=True)

        self._thread.start()



    def _run_async_loop(self, nickname):

        self._loop = asyncio.new_event_loop()

        asyncio.set_event_loop(self._loop)

        

        self.bot = pytalk.TeamTalkBot(client_name="GutsyDawn Voice")

        

        @self.bot.event

        async def on_my_login(server):

            await asyncio.sleep(2)

            self.tt_instance = server.teamtalk_instance

            tt = self.tt_instance

            

            try:

                tt.set_input_device("default")

                devices = tt.get_sound_devices()
                import wx
                wx.CallAfter(self.manager.update_audio_devices, devices)

                default_out = -1

                if len(devices) > 0:

                    default_out = devices[0].id

                    for d in devices:

                        if 'Output' in str(d):

                            default_out = d.id

                            break

                

                tt.super.initSoundOutputDevice(default_out)
                self.set_voice_volume(int(getattr(self.manager.player, 'voice_volume', 1.0) * 100))

                tt.enable_voice_transmission(self.mic_active)

                

                channel_password = "cliend10104040101010404040"

                joined = False

                

                try:

                    # Bergabung langsung ke Channel ID 8 sesuai instruksi user

                    target_ch_id = 8

                    tt.join_channel_by_id(target_ch_id, channel_password)

                    joined = True

                    

                except Exception as e:

                    import logging

                    logging.error(f"Gagal join channel ID 8: {e}")

                

                self.connected = joined
                # Dihilangkan speak keberhasilan join untuk menghindari "voice chat konengtit"
                if joined:
                    import wx
                    wx.CallAfter(self.manager.audio.play, "welcome.ogg")
                    wx.CallAfter(self.manager.tts.speak, f"Selamat datang kembali, {self.manager.player.username}!")

            except Exception as e:

                pass



        @self.bot.event

        async def on_ready():

            server_info = pytalk.TeamTalkServerInfo(

                host="tt5.angelsclan.net",

                tcp_port=63217,

                udp_port=63217,

                username="GutsyDawn_Cliend",

                password="GutsyDawn_Cliend6969",

                encrypted=False,

                nickname=nickname

            )

            await self.bot.add_server(server_info)

            

        @self.bot.event

        async def on_message(message):

            try:

                msg_type = "UNKNOWN"

                if "BroadcastMessage" in str(type(message)):

                    msg_type = "BROADCAST"

                elif "ChannelMessage" in str(type(message)):

                    msg_type = "CHANNEL"

                elif "UserMessage" in str(type(message)):

                    msg_type = "USER"

                    

                if msg_type in ["BROADCAST", "CHANNEL", "USER"]:

                    sender_name = message.user.nickname if message.user else "System"

                    content = message.content

                    import wx

                    # Putar notifikasi suara lokal dan tts

                    wx.CallAfter(self.manager.audio.play, "pesan_lokal.ogg")

                    wx.CallAfter(self.manager.tts.speak, f"[TT {msg_type}] {sender_name}: {content}")

            except:

                pass



        async def main_task():

            import logging

            logging.info("Starting TeamTalk bot connection...")

            try:

                async with self.bot:

                    await self.bot._start()

            except Exception as e:

                import traceback

                logging.error("Inner Exception: " + traceback.format_exc())

                

        try:
            self._loop.run_until_complete(main_task())
        except RuntimeError as e:
            if "Event loop stopped" in str(e):
                pass
            else:
                import logging, traceback
                logging.error("FATAL TEAMTALK ERROR: " + traceback.format_exc())
        except Exception as e:
            import logging, traceback
            logging.error("FATAL TEAMTALK ERROR: " + traceback.format_exc())



    def toggle_mic(self):

        self.mic_active = not self.mic_active

        if self.tt_instance:

            try:

                self.tt_instance.enable_voice_transmission(self.mic_active)

                status = "Mic aktif" if self.mic_active else "Mic mati"

                self.manager.tts.speak(status)

            except:

                pass



    def set_voice_volume(self, percentage: int):
        if self.tt_instance:
            try:
                from pytalk._utils import percent_to_ref_volume
                from pytalk.implementation.TeamTalkPy import TeamTalk5 as sdk
                internal_vol = percent_to_ref_volume(float(percentage))
                sdk._SetSoundOutputVolume(self.tt_instance._tt, internal_vol)
            except Exception:
                pass

    def stop(self):
        if self.is_running:
            self.is_running = False
            try:
                if getattr(self, 'tt_instance', None):
                    self.tt_instance.disconnect()
            except:
                pass
            if self._loop:
                self._loop.call_soon_threadsafe(self._loop.stop)


















