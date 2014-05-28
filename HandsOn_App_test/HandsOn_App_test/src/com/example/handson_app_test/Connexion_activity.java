package com.example.handson_app_test;

import android.app.Activity;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.os.Bundle;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.AdapterView;
import android.widget.AdapterView.OnItemClickListener;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.ListView;
import android.widget.Toast;

import java.util.ArrayList;

public class Connexion_activity extends Activity implements OnClickListener {

	private Button display_button;
	public static ArrayList<String> mac_array = new ArrayList<String>();
	private ListView bluetooth_device_listView;
	private BluetoothAdapter bluetooth_adapteur;
	private IntentFilter intent_bluetooth_filter;
	private Receiver receiver;

	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		init_view();
		init_listeners();
		init_bluetooth();
	}

	private final void init_view() {
		setContentView(R.layout.connection_settings_main);
		bluetooth_device_listView = (ListView) findViewById(R.id.bluetooth_device_listView);
		display_button = (Button) findViewById(R.id.display_button);
	}

	private final void init_listeners() {
		display_button.setOnClickListener(this);
	}

	private final void init_bluetooth() {

		bluetooth_adapteur = BluetoothAdapter.getDefaultAdapter();

		if (bluetooth_adapteur == null) {
			Toast.makeText(this, "Le bluetooth n'est pas supporté par l'application", Toast.LENGTH_LONG).show();
		}
		if (!bluetooth_adapteur.isEnabled()) {
			Toast.makeText(this, "Activation du bluetooth", Toast.LENGTH_LONG).show();
			Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
			startActivityForResult(enableBtIntent, 1);
		}

		bluetooth_adapteur.startDiscovery();
		intent_bluetooth_filter = new IntentFilter(BluetoothDevice.ACTION_FOUND);
		receiver = new Receiver();
		registerReceiver(receiver, intent_bluetooth_filter);

	}

	@Override
	public void onClick(View v) {

		switch (v.getId()) {

		case R.id.display_button:
			final ArrayAdapter<String> adapter = new ArrayAdapter<String>(this, android.R.layout.simple_list_item_1, mac_array);
			bluetooth_device_listView.setAdapter(adapter);
			bluetooth_device_listView.setOnItemClickListener(new OnItemClickListener() {
				@Override
				public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

					String g = (String) adapter.getItem(position);
					Intent intent = new Intent(getBaseContext(), Control_activity.class);
					intent.putExtra("btDeviceInfomration", g);
					startActivityForResult(intent, 1000);
				}
			});
			break;
		}
	}

	public class Receiver extends BroadcastReceiver {

		@Override
		public void onReceive(Context context, Intent intent) {

			String action = intent.getAction();

			if (BluetoothDevice.ACTION_FOUND.equals(action)) {

				BluetoothDevice device = (BluetoothDevice) intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
				mac_array.add("Nom : " + device.getName() + " ; Adresse MAC : " + device.getAddress());

			}

		}

	}

}