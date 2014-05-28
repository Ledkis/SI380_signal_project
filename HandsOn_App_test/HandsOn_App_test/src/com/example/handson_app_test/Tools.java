package com.example.handson_app_test;

import android.widget.TextView;

public class Tools {

	
	public static String[] intent_split(String string){
		
		String[] intentInfomrationTab = string.split(" ; ");
		
		String btDeviceNameInformation = intentInfomrationTab[0];
		String btDeviceMacAdressInformation = intentInfomrationTab[1];
		
		String[] btDeviceNameInformationTab = btDeviceNameInformation.split(" : ");
		String[] btDeviceMacAdressInformationTab = btDeviceMacAdressInformation.split(" : ");
		
		String[] btDeviceInformationTab = new String[2];
		
		btDeviceInformationTab[0] = btDeviceNameInformationTab[1];
		btDeviceInformationTab[1] = btDeviceMacAdressInformationTab[1];
		
		return btDeviceInformationTab;
	}
	
	public static String byteTabToString(byte[] bs){
		
		int i;
		String string = "";
		for(i=0; i<bs.length;i++){
			string = string + " ; " + bs[i];
		}
		
		return string;
		}
	
	public static void activityStateDisplay(int compteur, TextView connectionStateView, String state){
		compteur++;
		connectionStateView.setText(compteur + " : "+ state);
	}
	
}
