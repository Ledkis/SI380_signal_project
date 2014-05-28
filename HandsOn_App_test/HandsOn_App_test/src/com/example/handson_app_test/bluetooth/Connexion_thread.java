package com.example.handson_app_test.bluetooth;

import java.io.IOException;
import java.io.OutputStream;

import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;

public final class Connexion_thread extends Thread {

	private final BluetoothDevice bluetooth_device;
	private final BluetoothSocket socket;
	private Bluetooth_connexion bluetooth_connexion;
	private OutputStream sendStream = null;

	public Connexion_thread(Bluetooth_connexion connexion, BluetoothDevice device) {
		
		/*On garde une réfrence sur la connexion*/
		this.bluetooth_connexion = connexion;
		
		// Use a temporary object that is later assigned to mmSocket,
		// because mmSocket is final
		BluetoothSocket tmp_bt_socket = null;
		bluetooth_device = device;

		/* Get a BluetoothSocket to connect with the given BluetoothDevice */
		try {
			// MY_UUID is the app's UUID string, also used by the server
			// code
			tmp_bt_socket = device
					.createRfcommSocketToServiceRecord(Bluetooth_connexion.BT_UUID);
		} catch (IOException e) {
		}
		socket = tmp_bt_socket;
		try {
			sendStream = socket.getOutputStream();
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}

	public BluetoothSocket getSocket() {
		return socket;
	}

	public void run() {
		/* Cancel discovery because it will slow down the connection */
		bluetooth_connexion.getBluetooth_adapter().cancelDiscovery();
		try {
			// Connect the device through the socket. This will block
			// until it succeeds or throws an exception

			socket.connect();
		} catch (IOException connectException) {
		}

	}

	public void stopConnection() {
		try {
			socket.close();
		} catch (IOException e) {
		}
	}

	public final void send(String data) throws IOException {
		
		sendStream.write(data.getBytes());
		sendStream.flush();
	}
	
	public final void send_bytes(byte[] buffer) throws IOException {
		
		sendStream.write(buffer);
		sendStream.flush();
	}

}
