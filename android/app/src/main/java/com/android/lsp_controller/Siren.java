package com.android.lsp_controller;

import android.app.Activity;
import android.app.NotificationManager;
import android.content.Context;
import android.os.Bundle;
import android.os.Vibrator;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.ImageView;

import androidx.annotation.Nullable;

import com.bumptech.glide.Glide;
import com.bumptech.glide.request.target.GlideDrawableImageViewTarget;

public class Siren extends Activity {
    Vibrator vibrator;
    final Activity mainActivity = this;
    NotificationManager manager = MainActivity.manager;
    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        setContentView(R.layout.siren);

        ImageView siren = findViewById(R.id.siren_image);
        GlideDrawableImageViewTarget siren_gif = new GlideDrawableImageViewTarget(siren);
        Glide.with(mainActivity).load(R.drawable.siren).into(siren_gif);

        vibrator = (Vibrator)getSystemService(Context.VIBRATOR_SERVICE);
        Button dialogClose = findViewById(R.id.siren_close);
        dialogClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                manager.cancelAll();
                vibrator.cancel();
                finish();
            }
        });
        vibrator.vibrate(new long[]{1000,1000}, 0);
    }

    @Override
    public void onBackPressed() {
        // super.onBackPressed();
    }
}
