# KETUA (Core MQTT Connection)
# Mengatur koneksi ke broker, langganan saluran, dan pengiriman pesan.
import paho.mqtt.client as mqtt
import random
import logging

class KetuaMQTT:
    def __init__(self, wakil):
        self.wakil = wakil
        self.client_id = f"Pemain_GD_{random.randint(1000, 99999)}"
        self.is_connected = False
        
        try:
            from paho.mqtt.enums import CallbackAPIVersion
            self.client = mqtt.Client(CallbackAPIVersion.VERSION2, client_id=self.client_id)
        except ImportError:
            self.client = mqtt.Client(client_id=self.client_id)
            
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, *args, **kwargs):
        self.is_connected = True
        self.langganan_ulang()

    def on_disconnect(self, client, userdata, flags_or_rc, *args, **kwargs):
        self.is_connected = False

    def langganan_ulang(self):
        if self.is_connected:
            for saluran in self.wakil.dapatkan_daftar_saluran():
                try:
                    self.client.subscribe(saluran)
                except Exception as e:
                    logging.error(f"Gagal subscribe saluran {saluran}: {e}")
            
    def on_message(self, client, userdata, msg):
        try:
            payload = msg.payload.decode('utf-8')
            self.wakil.proses_pesan_masuk(msg.topic, payload)
        except Exception as e:
            logging.error(f"Gagal proses pesan MQTT: {e}")
        
    def sambungkan(self):
        if self.is_connected:
            self.langganan_ulang()
            return
        try:
            self.client.connect("broker.hivemq.com", 1883, 60)
            self.client.loop_start()
        except Exception as e:
            logging.error(f"Gagal menyambung radio MQTT: {e}")
            
    def putuskan(self):
        try:
            self.client.loop_stop()
            self.client.disconnect()
        except:
            pass
        self.is_connected = False
        
    def kirim_pesan(self, saluran, teks):
        if not self.is_connected:
            self.sambungkan()
        try:
            self.client.publish(saluran, teks)
        except Exception as e:
            logging.error(f"Gagal kirim pesan ke {saluran}: {e}")
