package com.android.lsp_controller;

import android.app.ActivityManager;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.os.Build;

import androidx.annotation.RequiresApi;

import java.util.List;

public class notificationBroadcast extends BroadcastReceiver {
    @RequiresApi(api = Build.VERSION_CODES.O)
    @Override
    public void onReceive(Context context, Intent intent) {
        ActivityManager am = (ActivityManager) context.getSystemService(Context.ACTIVITY_SERVICE);
        List<ActivityManager.RunningTaskInfo> tasks = am.getRunningTasks(Integer.MAX_VALUE);
        if (!tasks.isEmpty()) {
            int tasksSize = tasks.size();
            for (int i = 0; i < tasksSize; i++) {
                ActivityManager.RunningTaskInfo taskinfo = tasks.get(i);
                assert taskinfo.topActivity != null;
                if (taskinfo.topActivity.getPackageName().equals(context.getApplicationContext().getPackageName())) {
                    Intent intent1 = new Intent(Intent.ACTION_CLOSE_SYSTEM_DIALOGS);
                    context.getApplicationContext().sendBroadcast(intent1);
                    am.moveTaskToFront(taskinfo.id, 0);
                }
            }
        }
    }
}