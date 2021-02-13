package com.android.lsp_controller;

import android.Manifest;
import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.bluetooth.BluetoothSocket;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import java.io.IOException;
import java.io.OutputStream;
import java.util.ArrayList;
import java.util.UUID;

public class BluetoothCommunicationManager {
    private enum DeviceInfoType { DEVICE_NAME, DEVICE_ADDRESS }

    private final static String _UUID = "00000000-1111-2222-3333-444444444444";

    private BluetoothSocket btSocket;

    BluetoothCommunicationManager(Context context) {
        if (ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH) != PackageManager.PERMISSION_GRANTED
            && ActivityCompat.checkSelfPermission(context, Manifest.permission.BLUETOOTH_ADMIN) != PackageManager.PERMISSION_GRANTED)
        {
            ((MainActivity) context).requestPermissions(
                    new String[]{Manifest.permission.BLUETOOTH, Manifest.permission.BLUETOOTH_ADMIN},
                    MainActivity.REQUEST_PERMISSION_BLUETOOTH_NOT_GRANTED
            );
        }

        BluetoothAdapter btAdapter = BluetoothAdapter.getDefaultAdapter();
        if(btAdapter.isEnabled()) {
            Intent enableBluetoothIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
            ((AppCompatActivity) context).startActivityForResult(enableBluetoothIntent, MainActivity.REQUEST_INTENT_ENABLE_BLUETOOTH);
        }
    }

    private Object[] getPairedDevicesInfoArray(DeviceInfoType whatTypeYouWant) {
        BluetoothAdapter btAdpater = BluetoothAdapter.getDefaultAdapter();

        ArrayList<Object> pairedDeviceAddresses = new ArrayList<>();
        for(BluetoothDevice btDevice : btAdpater.getBondedDevices()) {
            Object youWant = btDevice;

            if(whatTypeYouWant == DeviceInfoType.DEVICE_ADDRESS) {
                youWant = btDevice.getAddress();
            }
            else if(whatTypeYouWant == DeviceInfoType.DEVICE_NAME) {
                youWant = btDevice.getName();
            }

            pairedDeviceAddresses.add(youWant);
        }

        //noinspection ToArrayCallWithZeroLengthArrayArgument
        return pairedDeviceAddresses.toArray(new Object[pairedDeviceAddresses.size()]);
    }

    public String[] getPairedDevicesName() {
        Object[] devList = getPairedDevicesInfoArray(DeviceInfoType.DEVICE_NAME);
        String[] devStrList = new String[devList.length];
        for(int i = 0; i < devList.length; i++) devStrList[i] = (String) devList[i];
        return devStrList;
    }

    public void connectTo(int index) throws Exception {
        if(btSocket != null && btSocket.isConnected()) return;

        BluetoothDevice btDevice = (BluetoothDevice) getPairedDevicesInfoArray(null)[index];

        btSocket = btDevice.createRfcommSocketToServiceRecord(UUID.fromString(_UUID));
        btSocket.connect();

        OutputStream sendStream = btSocket.getOutputStream();
        sendStream.write(0);
    }

    public void sendData(byte[] msgData) throws Exception {
        OutputStream sendStream = btSocket.getOutputStream();
        sendStream.write(ProtocolHelper.joinBytesArrays(new byte[][]{msgData}));
    }

    public void close() throws IOException {
        if(btSocket != null) {
            btSocket.close();
            btSocket = null;
        }
    }

    public boolean isConnect() {
        return btSocket != null && btSocket.isConnected();
    }
}
