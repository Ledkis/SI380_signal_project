package com.example.handson_app_test;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.view.View;
import android.view.View.OnClickListener;

/**
 * Classe contenant les control event de l'utiliateur et est à l'écoute de ces
 * derniers
 */
public class Control_listener implements OnClickListener, SensorEventListener {

	private Control_activity control_activity;

	private String gesture;

    // Some flags
	boolean gesture_f = false;
	boolean continuous_mode_f = false;
	boolean apprentissage_f = false;

	public Control_listener(Control_activity control_activity) {
		super();
		this.control_activity = control_activity;
	}

	public void onSensorChanged(SensorEvent acc_value) {
		String x_s = (Float.valueOf(acc_value.values[0])).toString();
		String y_s = (Float.valueOf(acc_value.values[1])).toString();
		String z_s = (Float.valueOf(acc_value.values[2])).toString();

        gesture = x_s + ";" + y_s + ";" + z_s + "\n";
        if(!apprentissage_f) {
            gesture = "gesture" + ";" + gesture;
        }
        else{
            gesture = "app" + ";" + gesture;
        }


		if(!control_activity.isConnected())
			return;
		if (gesture_f) {
			send(gesture);
		}

	}

	public void onAccuracyChanged(Sensor sensor, int accuracy) {
	}

	@Override
	public void onClick(View v) {

		switch (v.getId()) {
		
		case R.id.gce_button:
			if (gesture_f) {
				control_activity.getGce_button().setBackgroundColor(control_activity.getResources().getColor(R.color.aquisition_color));
                gesture_f = false;
                send("end_data\n");
			} else {
				control_activity.getGce_button().setBackgroundColor(control_activity.getResources().getColor(R.color.non_aquisition_color));
                gesture_f = true;
			}
			break;

            case R.id.continuous_recognition_button:
                if (continuous_mode_f) {
                    control_activity.getContinuous_recognition_button().setBackgroundColor(control_activity.getResources().getColor(R.color.aquisition_color));
                    continuous_mode_f = false;
                    send("end_continuous\n");

                } else {
                    control_activity.getContinuous_recognition_button().setBackgroundColor(control_activity.getResources().getColor(R.color.non_aquisition_color));
                    continuous_mode_f = true;
                    send("start_continuous\n");
                }
                break;

		case R.id.apprentissage_button:
			if (apprentissage_f) {
                control_activity.getApprentissage_button().setBackgroundColor(control_activity.getResources().getColor(R.color.aquisition_color));
                apprentissage_f = false;

                String gesture_name = control_activity.getGesture_name_edittext().getText().toString();

                if (gesture_name.equals("")){
                    gesture_name = "gesture";
                }
                send("end_app;" + gesture_name + "\n");

			} else {
                control_activity.getApprentissage_button().setBackgroundColor(control_activity.getResources().getColor(R.color.non_aquisition_color));
                apprentissage_f = true;
                send("start_app\n");
			}
			break;
		}
	}

    private void send(String msg){
        if (control_activity.isConnected()){
            control_activity.getBluetooth_connexion().send(msg);
        }
    }
}
