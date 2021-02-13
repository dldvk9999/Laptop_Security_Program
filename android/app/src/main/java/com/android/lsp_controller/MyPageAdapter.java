package com.android.lsp_controller;

import android.content.Context;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.viewpager.widget.PagerAdapter;

public class MyPageAdapter extends PagerAdapter {

    Context mContext;
    int resId = 0;
    String mchooseOne;

    public MyPageAdapter(Context context, String chooseOne) {
        mchooseOne = chooseOne;
        mContext = context;
    }

    @NonNull
    public Object instantiateItem(@NonNull ViewGroup collection, int position) {
        LayoutInflater inflater = LayoutInflater.from(mContext);
        switch (mchooseOne) {
            case "bluetooth":
                switch (position) {
                    case 0:
                        resId = R.layout.how_to_use_bluetooth_1;
                        break;
                    case 1:
                        resId = R.layout.how_to_use_bluetooth_2;
                        break;
                }
                break;

            case "voice_recognition":
                switch (position) {
                    case 0:
                        resId = R.layout.how_to_use_voicerecognition_1;
                        break;
                    case 1:
                        resId = R.layout.how_to_use_voicerecognition_2;
                        break;
                }
                break;

            case "password_recognition":
                switch (position) {
                    case 0:
                        resId = R.layout.how_to_use_password_1;
                        break;
                    case 1:
                        resId = R.layout.how_to_use_password_2;
                        break;
                }
                break;

            case "wifi_setting":
                switch (position) {
                    case 0:
                        resId = R.layout.how_to_use_wifi_1;
                        break;
                    case 1:
                        resId = R.layout.how_to_use_wifi_2;
                        break;
                }
                break;
        }
        ViewGroup layout = (ViewGroup) inflater.inflate(resId, collection, false);
        collection.addView(layout);
        return layout;
    }

    @Override
    public int getCount() { return 2; }

    @Override
    public boolean isViewFromObject(@NonNull View arg0, @NonNull Object arg1) { return arg0 == arg1; }
}