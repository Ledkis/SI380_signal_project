package com.example.handson_app_test;

import android.app.Activity;
import android.content.Intent;
import android.hardware.Sensor;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.widget.Button;
import android.widget.EditText;

import com.example.handson_app_test.bluetooth.Bluetooth_connexion;

public class Control_activity extends Activity {
	
	public static long start_time;

	private Bluetooth_connexion bluetooth_connexion;
	private boolean isConnected = false;

	private SensorManager sensor_manager;
	private Sensor accelerometre;
	
	/*Référence sur le gce actionners*/
	private Button gce_button;
	private Button continuous_recognition_button;
	private Button apprentissage_button;

    /*Référence sur gesture_name_edittext*/

    private EditText gesture_name_edittext;

	/*Listener sur les controls de l'utilisateur*/
	
	private Control_listener control_listener;
	
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		
		start_time = System.currentTimeMillis();

		init_view();
		init_listeners();
		init_accelerometer();

		/* On récupère les données envoyées par l'activitée mère */
		Intent intent1 = getIntent();
		/* On récupère les informations véhiculée par l'intent */
		String intent_info = intent1.getStringExtra("btDeviceInfomration");
		String[] intentInfomrationTab = Tools.intent_split(intent_info);
		bluetooth_connexion = new Bluetooth_connexion(intentInfomrationTab[0], intentInfomrationTab[1]);

	}

	private final void init_view() {
		setContentView(R.layout.control_view);
		
		/*initialisation de gce actionner*/
		gce_button = (Button) findViewById(R.id.gce_button);

        continuous_recognition_button = (Button) findViewById(R.id.continuous_recognition_button);

        apprentissage_button = (Button) findViewById(R.id.apprentissage_button);

        gesture_name_edittext = (EditText) findViewById(R.id.gesture_name_edittext);

	}
	
	private final void init_listeners() {
		control_listener = new Control_listener(this);
		
		/*Pour le gce actionners*/
		gce_button.setOnClickListener(control_listener);
        continuous_recognition_button.setOnClickListener(control_listener);
        apprentissage_button.setOnClickListener(control_listener);

	}

	private final void init_accelerometer() {
		sensor_manager = (SensorManager) getSystemService(this.SENSOR_SERVICE);
		accelerometre = sensor_manager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
		sensor_manager.registerListener(control_listener, accelerometre, SensorManager.SENSOR_DELAY_GAME);
	}

	@Override
	public boolean onCreateOptionsMenu(Menu menu) {
		super.onCreateOptionsMenu(menu);
		MenuInflater inflater = getMenuInflater();
		// R.menu.menu est l'id de notre menu
		inflater.inflate(R.menu.control_menu, menu);
		return true;
	}
	
	@Override
	public boolean onOptionsItemSelected (MenuItem item)
	{
	  switch(item.getItemId())
	  {
	    case R.id.connect_item:
	    	bluetooth_connexion.start();
	    	isConnected = true;
	      return true;
	  }
	  return super.onOptionsItemSelected(item);
	}


	public Bluetooth_connexion getBluetooth_connexion() {
		return bluetooth_connexion;
	}

	public SensorManager getSensor_manager() {
		return sensor_manager;
	}

	public Button getGce_button() {
		return gce_button;
	}

    public Button getContinuous_recognition_button() {
        return continuous_recognition_button;
    }

    public Button getApprentissage_button() {
		return apprentissage_button;
	}

    public EditText getGesture_name_edittext() {
		return gesture_name_edittext;
	}

	public boolean isConnected() {
		return isConnected;
	}

	
	

}
