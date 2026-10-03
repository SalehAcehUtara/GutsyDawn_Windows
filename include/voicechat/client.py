import sys
import os
import sys

if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")


if len(sys.argv) < 3:
    sys.exit(0)

import asyncio
import traceback
import json
import time

app_data_dir = sys.argv[2].replace('"', '') if len(sys.argv) > 2 else os.getcwd()
log_file = os.path.join(app_data_dir, "voice_client_log.txt")

with open(log_file, "w", encoding="utf-8") as f:
    f.write("Starting voice client...\n")

try:
    sys.path.append(r'D:\File\Bot\TeamTalk Bot\teamtalk-telegram-sender\.venv\Lib\site-packages')
    import pytalk

    async def main():
        nickname = sys.argv[1].replace('"', '') if len(sys.argv) > 1 else "Player"
        
        status_file = os.path.join(app_data_dir, "tt_status.json")
        cmd_file = os.path.join(app_data_dir, "tt_cmd.txt")
        heartbeat_file = os.path.join(app_data_dir, "tt_heartbeat.txt")
        
        if os.path.exists(status_file): os.remove(status_file)
        if os.path.exists(cmd_file): os.remove(cmd_file)
        if os.path.exists(heartbeat_file):
            with open(heartbeat_file, "w") as f: f.write("1")

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"Nickname: {nickname}\n")

        bot = pytalk.TeamTalkBot(client_name="GutsyDawn Voice")
        global_tt_instance = None
        global_tt_server = None
        mic_active = False
        
        def update_status(connected=False):
            if not global_tt_instance:
                return
            try:
                tt = global_tt_instance
                devices = tt.get_sound_devices()
                current_mic_name = "Default"
                
                mic_ids = []
                mic_names = []
                
                for d in devices:
                    if 'Input' in str(d) or 'Capture' in str(d) or 'Microphone' in str(d):
                        mic_ids.append(str(d.id))
                        mic_names.append(d.name.replace("|", ""))
                        if d.id == tt._current_input_device_id:
                            current_mic_name = d.name
                            
                status = {
                    "connected": connected,
                    "mic_active": mic_active,
                    "current_mic": current_mic_name,
                    "mic_ids": ",".join(mic_ids),
                    "mic_names": "|".join(mic_names)
                }
                with open(status_file, "w", encoding="utf-8") as f:
                    json.dump(status, f)
            except Exception as e:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"Error update status: {e}\n")

        @bot.event
        async def on_my_login(server):
            nonlocal global_tt_instance
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"Logged in to Voice Server as {nickname}! Waiting for channel list...\n")
            
            await asyncio.sleep(2)
            
            global_tt_instance = server.teamtalk_instance
            global_tt_server = server
            tt = global_tt_instance
            
            try:
                tt.set_input_device("default")
                
                devices = tt.get_sound_devices()
                default_out = -1
                if len(devices) > 0:
                    default_out = devices[0].id
                    for d in devices:
                        if 'Output' in str(d):
                            default_out = d.id
                            break
                
                tt.super.initSoundOutputDevice(default_out)
                tt.enable_voice_transmission(mic_active)
                
                channel_password = "cliend10104040101010404040"
                joined = False
                
                try:
                    ch_id = tt.super.getChannelIDFromPath("/Gutsy Dawn/Cliend_NVGT/")
                    if ch_id <= 1:
                        ch_id = tt.super.getChannelIDFromPath("/Gutsy Dawn/Cliend_NVGT")
                    
                    if ch_id > 1:
                        tt.join_channel_by_id(ch_id, channel_password)
                        joined = True
                        with open(log_file, "a", encoding="utf-8") as f:
                            f.write(f"Joined via exact path. ID: {ch_id}\n")
                except Exception as ex:
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write(f"Path join error: {ex}\n")
                
                if not joined:
                    for i in range(2, 5000):
                        try:
                            ch = tt.get_channel(i)
                            if "Cliend" in ch.name or "NVGT" in ch.name:
                                tt.join_channel_by_id(i, channel_password)
                                joined = True
                                with open(log_file, "a", encoding="utf-8") as f:
                                    f.write(f"Joined via fallback scan. ID: {i}, Name: {ch.name}\n")
                                break
                        except:
                            pass
                
                if joined:
                    update_status(connected=True)
                else:
                    with open(log_file, "a", encoding="utf-8") as f:
                        f.write("Error init audio: Channel not found (scanned 2 to 5000)\n")
                        
            except Exception as e:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"Error init audio: {e}\n")

        @bot.event
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
            await bot.add_server(server_info)

        
        @bot.event
        async def on_message(message):
            try:
                msg_type = "UNKNOWN"
                if "BroadcastMessage" in str(type(message)):
                    msg_type = "BROADCAST"
                elif "ChannelMessage" in str(type(message)):
                    msg_type = "CHANNEL"
                elif "UserMessage" in str(type(message)):
                    msg_type = "USER"
                
                # Kita ambil pesan broadcast dan channel aja
                if msg_type in ["BROADCAST", "CHANNEL", "USER"]:
                    sender_name = message.user.nickname if message.user else "System"
                    content = message.content
                    
                    recv_file = os.path.join(app_data_dir, "tt_recv.txt")
                    with open(recv_file, "a", encoding="utf-8") as f:
                        f.write(f"{msg_type}|{sender_name}|{content}\n")
                        
            except Exception as e:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write(f"Error on_message: {e}\n")

        async def command_listener():
            nonlocal mic_active, global_tt_instance
            while True:
                if os.path.exists(heartbeat_file):
                    if time.time() - os.path.getmtime(heartbeat_file) > 300:
                        with open(log_file, "a", encoding="utf-8") as f:
                            f.write("Heartbeat timeout (NVGT closed). Exiting client.\n")
                        os._exit(0)
                        
                if os.path.exists(cmd_file) and global_tt_instance:
                    try:
                        with open(cmd_file, "r", encoding="utf-8") as f:
                            cmd = f.read().strip()
                        os.remove(cmd_file)
                        
                        if cmd == "TOGGLE_MIC":
                            mic_active = not mic_active
                            global_tt_instance.enable_voice_transmission(mic_active)
                            update_status(connected=True)
                        elif cmd.startswith("SET_MIC:"):
                            dev_id = int(cmd.split(":")[1])
                            global_tt_instance.super.initSoundInputDevice(dev_id)
                            global_tt_instance._current_input_device_id = dev_id
                            update_status(connected=True)
                        elif cmd.startswith("MSG:"):
                            msg_content = cmd[4:]
                            try:
                                ch_id = global_tt_instance.getMyChannelID()
                                ch = global_tt_server.get_channel(ch_id)
                                if ch:
                                    ch.send_message(msg_content)
                            except Exception as e:
                                pass
                        elif cmd == "LEAVE":
                            global_tt_instance.logout()
                            global_tt_instance.disconnect()
                            if os.path.exists(status_file):
                                os.remove(status_file)
                            os._exit(0)
                    except Exception as e:
                        pass
                await asyncio.sleep(0.5)
        
        asyncio.create_task(command_listener())
        async with bot:
            await bot._start()

    asyncio.run(main())
except Exception as e:
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"CRITICAL ERROR: {traceback.format_exc()}\n")

