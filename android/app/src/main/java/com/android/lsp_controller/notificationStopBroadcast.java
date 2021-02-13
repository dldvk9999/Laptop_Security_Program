package com.android.lsp_controller;

import android.annotation.SuppressLint;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.os.Build;
import android.os.IBinder;
import android.util.Log;

import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.core.app.NotificationCompat;

public class notificationStopBroadcast extends Service {
    NotificationManager manager = MainActivity.manager;
    NotificationCompat.Builder builder;
    String CHANNEL_ID = "123456789";
    String CHANEL_NAME = "LSP_Controller";

    @RequiresApi(api = Build.VERSION_CODES.O)
    @SuppressLint("LongLogTag")
    @Override
    public void onCreate() {
        Log.w("notificationStopBroadcast", "STOP Signal!!!!!");

        builder = null;
        manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        //버전 오레오 이상일 경우
        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.O){
            @SuppressLint("WrongConstant")
            NotificationChannel channel = new NotificationChannel(CHANNEL_ID, CHANEL_NAME, NotificationManager.IMPORTANCE_MAX);
            channel.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
            manager.createNotificationChannel(channel);

            builder = new NotificationCompat.Builder(getApplicationContext(), CHANNEL_ID);

            //하위 버전일 경우
        } else {
            //noinspection deprecation
            builder = new NotificationCompat.Builder(getApplicationContext());
        }

        Intent intent = new Intent(getApplicationContext(), notificationBroadcast.class);
        PendingIntent pendingIntent = PendingIntent.getBroadcast(getApplicationContext(),0,
                intent, PendingIntent.FLAG_UPDATE_CURRENT);

        builder.setContentTitle("LSP 실행 중");
        builder.setContentText("알림창을 아래로 밀어 종료버튼을 터치하여 종료하세요.");
        builder.setSmallIcon(R.drawable.icon);
        builder.setPriority(NotificationCompat.PRIORITY_MAX);
        builder.setVisibility(NotificationCompat.VISIBILITY_PUBLIC);
        builder.setContentIntent(pendingIntent);
        Notification notification = builder.build();
        notification.flags = Notification.FLAG_AUTO_CANCEL;
        manager.notify(Integer.parseInt(CHANNEL_ID), notification);

        manager.cancelAll();

        android.os.Process.killProcess(android.os.Process.myPid());
        System.exit(0);

        super.onCreate();
    }

    @Nullable
    @Override
    public IBinder onBind(Intent rootIntent) { return null; }

    @Override
    public void onTaskRemoved(Intent rootIntent) {
        Log.e("Error", "onTaskRemoved - " + rootIntent);
        stopSelf();
    }
}
