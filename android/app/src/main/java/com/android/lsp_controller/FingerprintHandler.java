package com.android.lsp_controller;

import android.annotation.TargetApi;
import android.app.Activity;
import android.content.Context;
import android.hardware.fingerprint.FingerprintManager;
import android.os.Build;
import android.os.CancellationSignal;
import android.os.Handler;
import android.view.View;
import android.widget.TextView;

import androidx.core.content.ContextCompat;

@TargetApi(Build.VERSION_CODES.M)
public class FingerprintHandler extends FingerprintManager.AuthenticationCallback {
    CancellationSignal cancellationSignal;
    private Context context;

    @SuppressWarnings("deprecation")
    public FingerprintHandler(Context context){
        this.context = context;
    }

    public void startAuto(FingerprintManager fingerprintManager, FingerprintManager.CryptoObject cryptoObject){
        cancellationSignal = new CancellationSignal();
        fingerprintManager.authenticate(cryptoObject, cancellationSignal, 0, this, null);
    }

    @Override
    public void onAuthenticationError(int errorCode, CharSequence errString) {
        this.update("인증 에러 발생\n" + errString, false);
    }

    @Override
    public void onAuthenticationFailed() {
        this.update("인증 실패", false);
    }

    @Override
    public void onAuthenticationHelp(int helpCode, CharSequence helpString) {
        this.update("Error: "+ helpString, false);
    }

    @Override
    public void onAuthenticationSucceeded(FingerprintManager.AuthenticationResult result) {
        this.update("인증 성공!", true);
    }

    public void stopFingerAuth(){
        if(cancellationSignal != null && !cancellationSignal.isCanceled()){
            cancellationSignal.cancel();
        }
    }

    private void update(String s, boolean b) {
        final TextView tv_message = (TextView) ((Activity)context).findViewById(R.id.Finger_Auth);

        tv_message.setText(s);

        if(!b){
            tv_message.setVisibility(View.VISIBLE);
            tv_message.setTextColor(ContextCompat.getColor(context, R.color.design_default_color_error));
        } else { //지문인증 성공
            tv_message.setVisibility(View.VISIBLE);
            tv_message.setTextColor(ContextCompat.getColor(context, R.color.design_default_color_on_primary));
            //noinspection deprecation
            Handler handler = new Handler();
            handler.postDelayed(new Runnable() {
                @Override
                public void run() {
                    tv_message.callOnClick();
                }
            }, 1000);

        }
    }
}