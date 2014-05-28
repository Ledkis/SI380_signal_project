package com.example.handson_app_test.bluetooth;

import java.io.IOException;
import java.util.UUID;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;

public final class Bluetooth_connexion {
	
	private String server_name;
	private BluetoothDevice bluetooth_device;
	private Connexion_thread connexion;
	private BluetoothAdapter bluetooth_adapter;
	public final static UUID BT_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB");

	public Bluetooth_connexion(String server_name, String adresse){
		this.server_name = server_name;
		this.bluetooth_adapter = BluetoothAdapter.getDefaultAdapter();
		this.bluetooth_device = bluetooth_adapter.getRemoteDevice(adresse);
		this.connexion = new Connexion_thread(this, bluetooth_device);
		
	}

	public BluetoothAdapter getBluetooth_adapter() {
		return bluetooth_adapter;
	}
	
	public final void start(){
		connexion.run(); //TODO : Pourquoi mettre start ne marche pas
	}
	
	public final void send(String data){
		try {
			connexion.send(data);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	public final void send_byte(byte[] buffer){
		try {
			connexion.send_bytes(buffer);
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
