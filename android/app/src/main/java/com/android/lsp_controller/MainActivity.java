package com.android.lsp_controller;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.app.Dialog;
import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.os.Vibrator;
import android.util.Log;
import android.view.Menu;
import android.view.MenuInflater;
import android.view.MenuItem;
import android.view.View;
import android.view.Window;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.NotificationCompat;
import androidx.viewpager.widget.ViewPager;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.text.SimpleDateFormat;
import java.util.Date;

public class MainActivity extends AppCompatActivity {
    static final int REQUEST_PERMISSION_BLUETOOTH_NOT_GRANTED = 0;
    static final int REQUEST_INTENT_ENABLE_BLUETOOTH = 0;
    private EditText sendDataInput;
    private long time= 0;
    final Activity mainActivity = this;
    public static Boolean AuthState = false;
    public static Boolean backgroundExist = false;
    public static Boolean cancelAuth = false;

    private Socket socket;
    private DataOutputStream dos;
    private DataInputStream dis;
    private int port = 9999;
    public static boolean wifi_status = false;
    static boolean notiState = false;

    TextView wifi_log;
    Vibrator vibrator;

    public static NotificationManager manager;
    NotificationCompat.Builder builder;
    String CHANNEL_ID = "123456789";
    String CHANEL_NAME = "LSP_Controller";

    @SuppressLint("HandlerLeak")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        setTitle("Laptop Security Program Controller");

        vibrator = (Vibrator)getSystemService(Context.VIBRATOR_SERVICE);

        sendDataInput                                 = findViewById(R.id.sendDataInput);
        Button connectButton                          = findViewById(R.id.connect);
        Button sendDataButton                         = findViewById(R.id.sendData);
        Button Voice_Rec                              = findViewById(R.id.Voice_Rec);
        Button Password_Rec                           = findViewById(R.id.Password_Rec);
        final Button    closeButton                   = findViewById(R.id.close);
        final TextView  connectDevice                 = findViewById(R.id.connectDevice);
        final BluetoothCommunicationManager btCommMgr = new BluetoothCommunicationManager(this);
        wifi_log = findViewById(R.id.log_);

        connectButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(btCommMgr.isConnect()) {
                    Toast.makeText(mainActivity, "이미 연결되어 있습니다.", Toast.LENGTH_SHORT).show();
                    return;
                }

                AlertDialog.Builder showRemoteBtDevices = new AlertDialog.Builder(mainActivity);
                showRemoteBtDevices.setTitle("연결 가능한 장치");
                showRemoteBtDevices.setItems(btCommMgr.getPairedDevicesName(), new DialogInterface.OnClickListener() {
                        @Override
                        public void onClick(DialogInterface dialog, int which) {
                            try {
                                btCommMgr.connectTo(which);
                                Toast.makeText(mainActivity, btCommMgr.getPairedDevicesName()[which] + " 연결 성공", Toast.LENGTH_SHORT).show();
                                connectDevice.setText(btCommMgr.getPairedDevicesName()[which]);

                                notiState = true;
                                showNoti();
                            }
                            catch(Exception ioe) {
                                ioe.printStackTrace();
                                Toast.makeText(mainActivity, "디바이스 연결 실패\n" + ioe.toString(), Toast.LENGTH_LONG).show();
                            }
                        }
                    }
                );
                showRemoteBtDevices.show();
            }
        });

        closeButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(!btCommMgr.isConnect()) {
                    Toast.makeText(mainActivity, "노트북과 블루투스 연동을 먼저 해주세요.", Toast.LENGTH_SHORT).show();
                    return;
                }

                try {
                    btCommMgr.close();
                    connectDevice.setText("");
                    manager.cancelAll();
                    notiState = false;
                    Toast.makeText(mainActivity, "종료 성공", Toast.LENGTH_SHORT).show();
                }
                catch(IOException ioe) {
                    ioe.printStackTrace();
                    Toast.makeText(mainActivity,  "종료 실패\n" + ioe.toString(), Toast.LENGTH_LONG).show();
                }
            }
        });

        sendDataButton.setOnClickListener(new View.OnClickListener() {
            @RequiresApi(api = Build.VERSION_CODES.KITKAT)
            @Override
            public void onClick(View v) {
                if(!btCommMgr.isConnect()) {
                    Toast.makeText(mainActivity, "노트북과 블루투스 연동을 먼저 해주세요.", Toast.LENGTH_SHORT).show();
                    return;
                }

                String data = sendDataInput.getText().toString();
                data = data.replace(" ", "");
                if (data.equals("")) {
                    Toast.makeText(mainActivity, "메시지가 비어있습니다", Toast.LENGTH_SHORT).show();
                }
                else {
                    String encArray = null;
                    try {
                        encArray = AES256Cipher.AES_Encode(data);
                    } catch (InvalidKeyException | ArrayIndexOutOfBoundsException KeyException) {
                        KeyException.printStackTrace();
                        Toast.makeText(mainActivity, "전송 속도가 너무 빠릅니다.\n잠시 뒤 다시시도 해주세요.", Toast.LENGTH_LONG).show();
                    } catch (Exception e) {
                        e.printStackTrace();
                        Toast.makeText(mainActivity, "암호화 오류\n" + e.toString(), Toast.LENGTH_LONG).show();
                        return;
                    }

                    try {
                        assert encArray != null;
                        String CipherMessage = encArray.replace("\n", "");
                        byte[] msgdata = CipherMessage.getBytes(StandardCharsets.UTF_8);
                        // byte[] msgdata = sendDataInput.getText().toString().getBytes(StandardCharsets.UTF_8);
                        btCommMgr.sendData(msgdata);
                        sendDataInput.setText("");
                        Toast.makeText(mainActivity, "메시지 전송 완료", Toast.LENGTH_SHORT).show();
                    } catch (Exception e) {
                        e.printStackTrace();
                        Toast.makeText(mainActivity, "메시지 전송 실패\n" + e.toString(), Toast.LENGTH_LONG).show();
                    }
                }
            }
        });

        Voice_Rec.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(!btCommMgr.isConnect()) {
                    Toast.makeText(mainActivity, "노트북과 블루투스 연동을 먼저 해주세요.", Toast.LENGTH_SHORT).show();
                    return;
                }

                try {
                    String data = "Voice Recognition";
                    String encArray;
                    try {
                        encArray = AES256Cipher.AES_Encode(data);
                    } catch (Exception e) {
                        e.printStackTrace();
                        Toast.makeText(mainActivity, "암호화 오류\n" + e.toString(), Toast.LENGTH_LONG).show();
                        return;
                    }

                    String CipherMessage = encArray.replace("\n", "");
                    byte[] msgData = CipherMessage.getBytes(StandardCharsets.UTF_8);
                    // byte[] msgData = "Voice Recognition".getBytes(StandardCharsets.UTF_8);
                    btCommMgr.sendData(msgData);
                    Toast.makeText(mainActivity, "노트북 마이크에서 '잠금 해제'라고 말해주세요.", Toast.LENGTH_SHORT).show();
                } catch (Exception e) {
                    e.printStackTrace();
                    Toast.makeText(mainActivity, "음성인식 전송 실패\n" + e.toString(), Toast.LENGTH_LONG).show();
                }
            }
        });

        Password_Rec.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                if(!btCommMgr.isConnect()) {
                    Toast.makeText(mainActivity, "노트북과 블루투스 연동을 먼저 해주세요.", Toast.LENGTH_SHORT).show();
                    return;
                }

                try {
                    String data = "Password Recognition";
                    String encArray;
                    try {
                        encArray = AES256Cipher.AES_Encode(data);
                    } catch (Exception e) {
                        e.printStackTrace();
                        Toast.makeText(mainActivity, "암호화 오류\n" + e.toString(), Toast.LENGTH_LONG).show();
                        return;
                    }

                    String CipherMessage = encArray.replace("\n", "");
                    byte[] msgData = CipherMessage.getBytes(StandardCharsets.UTF_8);
                    // byte[] msgData = "Password Recognition".getBytes(StandardCharsets.UTF_8);
                    btCommMgr.sendData(msgData);
                    Toast.makeText(mainActivity, "노트북에서 비밀번호를 입력해주세요.", Toast.LENGTH_SHORT).show();
                } catch (Exception e) {
                    e.printStackTrace();
                    Toast.makeText(mainActivity, "비밀번호 인증 전송 실패\n" + e.toString(), Toast.LENGTH_LONG).show();
                }
            }
        });
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (AuthState) {
            Intent intent= new Intent(getApplicationContext(), Splash.class);
            startActivity(intent);
        }
        if (cancelAuth) {
            moveTaskToBack(true);
            cancelAuth = false;
            AuthState = true;
        } else {
            AuthState = false;
        }
    }

    @Override
    public void onConfigurationChanged(@SuppressWarnings("NullableProblems") Configuration newConfig) {
        super.onConfigurationChanged(newConfig);
        if(newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE){
            Toast.makeText(this, "LSP_Controller는 세로방향 전용 어플리케이션 입니다.\n화면을 돌려주세요.", Toast.LENGTH_LONG).show();
        }
    }

    @SuppressLint("WrongConstant")
    public void showNoti(){
        builder = null;
        manager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
        //버전 오레오 이상일 경우
        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.O){
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
        Intent intent2 = new Intent(getApplicationContext(), notificationStopBroadcast.class);

        intent.putExtra("LSP", android.os.Process.myPid());

        PendingIntent pendingIntent = PendingIntent.getBroadcast(getApplicationContext(),0,
                intent, PendingIntent.FLAG_UPDATE_CURRENT);
        PendingIntent stop = PendingIntent.getService(getApplicationContext(), 0,
                intent2, PendingIntent.FLAG_UPDATE_CURRENT);

        builder.setContentTitle("LSP 실행 중");
        builder.setTicker("LSP 연동 완료!");
        builder.setAutoCancel(true);
        builder.addAction(new NotificationCompat.Action(R.drawable.stop, "LSP 종료", stop));
        builder.setContentText("알림창을 아래로 밀어 종료버튼을 터치하여 종료하세요.");
        builder.setSmallIcon(R.drawable.icon);
        builder.setPriority(NotificationCompat.PRIORITY_MAX);
        builder.setVisibility(Notification.VISIBILITY_PUBLIC);
        builder.setContentIntent(pendingIntent);
        Notification notification = builder.build();
        notification.flags = Notification.FLAG_NO_CLEAR;
        manager.notify(Integer.parseInt(CHANNEL_ID), notification);
    }

    @Override
    public void onBackPressed(){
        if (notiState || wifi_status) {
            AuthState = true;
            backgroundExist = true;
            moveTaskToBack(true);
            Toast.makeText(mainActivity, "LSP 앱이 백그라운드로 전환되었습니다.", Toast.LENGTH_SHORT).show();
        } else {
            if (System.currentTimeMillis() - time >= 2000) {
                time = System.currentTimeMillis();
                Toast.makeText(getApplicationContext(), "뒤로 버튼을 한번 더 누르면 종료합니다.", Toast.LENGTH_SHORT).show();
            } else if (System.currentTimeMillis() - time < 2000) {
                finish();
                System.exit(0);
                android.os.Process.killProcess(android.os.Process.myPid());
            }
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        MenuInflater menuInflater = getMenuInflater();
        menuInflater.inflate(R.menu.menu, menu);
        return true;
    }

    @SuppressLint("SetTextI18n")
    @Override
    public boolean onOptionsItemSelected(final MenuItem item) {
        switch (item.getItemId()) {
            case R.id.developer:
                AlertDialog.Builder dlg = new AlertDialog.Builder(MainActivity.this);
                dlg.setIcon(R.drawable.icon);
                dlg.setTitle("Program Developers");
                dlg.setMessage("Mentor\t: 김지현 - General supervision\n" +
                        "Mentee\t: 최지원(Team Leader) - User recognition  module Dev.\n" +
                        "Mentee\t: 곽현석 - Device filter driver Dev.\n" +
                        "Mentee\t: 박종근 - Main GUI & core Dev.\n" +
                        "other\t\t\t: 최근영 - Sub Dev and help others.");

                dlg.setPositiveButton("확인", null);
                dlg.show();
                break;

            case R.id.Use_Bluetooth:
                showDialog("블루투스 연동 법", "bluetooth");
                break;

            case R.id.Use_Voice_Recognition:
                showDialog("음성인식 사용 법", "voice_recognition");
                break;

            case R.id.Use_Password_Recognition:
                showDialog("비밀번호인식 사용 법", "password_recognition");
                break;

            case R.id.Use_WIFI:
                showDialog("와이파이 사용 법", "wifi_setting");
                break;

            case R.id.Wifi:
                if (wifi_status) {
                    Toast.makeText(mainActivity, "이미 연결되어 있습니다.\n다시 하시려면 WIFI Close를 해주세요.", Toast.LENGTH_SHORT).show();
                } else {
                    final LinearLayout linearLayout = (LinearLayout) View.inflate(MainActivity.this, R.layout.ip_edit, null);
                    final EditText editText = linearLayout.findViewById(R.id.ip);
                    AlertDialog.Builder dialog = new AlertDialog.Builder(MainActivity.this);
                    dialog.setTitle("노트북 IP 주소 입력");
                    dialog.setView(linearLayout);

                    dialog.setPositiveButton("확인", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                            final String inputValue;
                            try {
                                inputValue = editText.getText().toString();
                            } catch (Exception e) {
                                Toast.makeText(mainActivity, "IP주소가 비어있습니다.\n다시 입력해주세요.", Toast.LENGTH_SHORT).show();
                                return;
                            }

                            Thread checkUpdate = new Thread() {
                                public void run() {
                                    try {
                                        socket = new Socket(inputValue, port);
                                    } catch (IOException e) {
                                        e.printStackTrace();
                                        MainActivity.this.runOnUiThread(new Runnable() {
                                            public void run() {
                                                Toast.makeText(MainActivity.this, "해당하는 IP주소로 통신할 수 없습니다.", Toast.LENGTH_SHORT).show();
                                            }
                                        });
                                        return;
                                    }

                                    MainActivity.this.runOnUiThread(new Runnable() {
                                        public void run() {
                                            wifi_status = true;
                                            notiState = true;
                                            showNoti();
                                            Log.d("LSP", "WIFI 연동 성공!");
                                            wifi_log.append("\n" + toastTime() + " WIFI 연동 성공!\n");
                                            Toast.makeText(MainActivity.this, "WIFI 연동 성공!", Toast.LENGTH_SHORT).show();
                                        }
                                    });

                                    try {
                                        Log.d("LSP", "서버로 연결요청 보냄");
                                        dos = new DataOutputStream(socket.getOutputStream());
                                        dis = new DataInputStream(socket.getInputStream());
                                        dos.writeUTF("안드로이드에서 서버로 연결요청");
                                    } catch (IOException e) {
                                        e.printStackTrace();
                                    }

                                    Looper.prepare();
                                    try {
                                        int line2;
                                        int signal = 0;
                                        while (true) {
                                            line2 = dis.read();

                                            if (line2 > signal) {
                                                Log.d("LSP", "서버 상태 정상");
                                                MainActivity.this.runOnUiThread(new Runnable() {
                                                    public void run() {
                                                        wifi_log.append(toastTime() + " 서버 상태 : 정상\n");
                                                    }
                                                });
                                            } else {
                                                socket.close();
                                                wifi_status = false;

                                                MainActivity.this.runOnUiThread(new Runnable() {
                                                    @SuppressLint("WrongConstant")
                                                    @RequiresApi(api = Build.VERSION_CODES.O)
                                                    public void run() {
                                                        showSirenDialog();
                                                        notiState = false;

                                                        manager.cancelAll();

                                                        wifi_log.append(toastTime() + " 소켓 종료\n");

                                                        NotificationManager sirenManager;
                                                        NotificationCompat.Builder sirenBuilder;

                                                        sirenManager = (NotificationManager) getSystemService(NOTIFICATION_SERVICE);
                                                        //버전 오레오 이상일 경우
                                                        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                                                            NotificationChannel channel = new NotificationChannel("LSP_Siren", "LSP_Siren", NotificationManager.IMPORTANCE_MAX);
                                                            channel.setLockscreenVisibility(Notification.VISIBILITY_PUBLIC);
                                                            sirenManager.createNotificationChannel(channel);

                                                            sirenBuilder = new NotificationCompat.Builder(getApplicationContext(), "LSP_Siren");

                                                            //하위 버전일 경우
                                                        } else {
                                                            //noinspection deprecation
                                                            sirenBuilder = new NotificationCompat.Builder(getApplicationContext());
                                                        }

                                                        Bitmap notiLargeIcon = BitmapFactory.decodeResource(getResources(), R.drawable.danger);

                                                        Intent intent = new Intent(getApplicationContext(), notificationBroadcast.class);
                                                        PendingIntent pendingIntent = PendingIntent.getBroadcast(getApplicationContext(), 0, intent, PendingIntent.FLAG_UPDATE_CURRENT);

                                                        sirenBuilder.setContentTitle("LSP 알림");
                                                        sirenBuilder.setAutoCancel(true);
                                                        sirenBuilder.setContentText("노트북과 와이파이 연결이 종료되었습니다!!");
                                                        sirenBuilder.setSmallIcon(R.drawable.stop);
                                                        sirenBuilder.setLargeIcon(notiLargeIcon);
                                                        sirenBuilder.setPriority(NotificationCompat.PRIORITY_HIGH);
                                                        sirenBuilder.setContentIntent(pendingIntent);
                                                        sirenBuilder.setFullScreenIntent(pendingIntent, true);
                                                        sirenBuilder.setVisibility(Notification.VISIBILITY_PUBLIC);
                                                        Notification notification_Siren = sirenBuilder.build();
                                                        notification_Siren.flags = Notification.FLAG_INSISTENT;
                                                        sirenManager.notify(Integer.parseInt("123456"), notification_Siren);

                                                        PowerManager pm = (PowerManager) getSystemService(Context.POWER_SERVICE);
                                                        //noinspection deprecation
                                                        @SuppressLint("InvalidWakeLockTag") final PowerManager.WakeLock wakeLock = pm.newWakeLock( PowerManager.SCREEN_DIM_WAKE_LOCK | PowerManager.ACQUIRE_CAUSES_WAKEUP, "TAG" );
                                                        wakeLock.acquire(5000);

                                                        //noinspection deprecation
                                                        new Handler().postDelayed(new Runnable() {
                                                            @Override
                                                            public void run() {
                                                                wakeLock.release();
                                                            }
                                                        }, 5000);
                                                    }
                                                });
                                                Log.d("LSP", "소켓 종료");
                                                break;
                                            }
                                            signal = -1;
                                        }
                                    } catch (Exception e) {
                                        try {
                                            socket.close();
                                            wifi_status = false;
                                            notiState = false;
                                            manager.cancelAll();
                                            Log.d("LSP", "소켓 종료");
                                        } catch (IOException ex) {
                                            ex.printStackTrace();
                                        }
                                    }
                                    Looper.loop();
                                }
                            };
                            checkUpdate.start();
                        }
                    }).setNegativeButton("취소", new DialogInterface.OnClickListener() {
                        public void onClick(DialogInterface dialog, int which) {
                            dialog.cancel();
                        }
                    });

                    dialog.show();
                }
                break;

            case R.id.Wifi_log:
                final TextView textView = findViewById(R.id.log_);
                final AlertDialog.Builder wifi_log = new AlertDialog.Builder(MainActivity.this);
                wifi_log.setIcon(R.drawable.icon);
                wifi_log.setTitle("wifi_log");
                wifi_log.setMessage(textView.getText().toString());
                wifi_log.setPositiveButton("확인", null);
                wifi_log.show();
                break;

            case R.id.wifi_close:
                if (socket == null) {
                    Toast.makeText(mainActivity, "먼저 WIFI를 연동해주세요.", Toast.LENGTH_SHORT).show();
                } else {
                    try {
                        socket.close();
                        TextView textView1 = findViewById(R.id.log_);
                        textView1.setText("");
                        wifi_status = false;
                        notiState = false;
                        manager.cancelAll();
                        Toast.makeText(mainActivity, "WIFI 연동 종료!", Toast.LENGTH_SHORT).show();
                    } catch (IOException e) {
                        e.printStackTrace();
                        Toast.makeText(mainActivity, "WIFI 연동 종료 실패\n" + e.toString(), Toast.LENGTH_SHORT).show();
                    }
                }
                break;
        }
        return super.onOptionsItemSelected(item);
    }

    public void showSirenDialog() {
        Intent intent= new Intent(getApplicationContext(), Siren.class);
        intent.addFlags(Intent.FLAG_ACTIVITY_TASK_ON_HOME);
        startActivity(intent);
    }

    public void showDialog(String title, String type) {
        final Dialog dialog = new Dialog(MainActivity.this);
        dialog.requestWindowFeature(Window.FEATURE_NO_TITLE);
        dialog.setContentView(R.layout.viewpager);
        dialog.setCanceledOnTouchOutside(false);

        MyPageAdapter adapter = new MyPageAdapter(MainActivity.this, type);
        ViewPager pager = dialog.findViewById(R.id.viewpager);
        TextView textView = dialog.findViewById(R.id.How_to_use_title);
        textView.setText(title);
        pager.setAdapter(adapter);

        Button dialogClose = dialog.findViewById(R.id.dialogClose);
        dialogClose.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                dialog.dismiss();
            }
        });

        dialog.show();
    }

    public String toastTime() {
        long now = System.currentTimeMillis();
        Date date = new Date(now);
        @SuppressLint("SimpleDateFormat")
        SimpleDateFormat sdfNow = new SimpleDateFormat("yyyy/MM/dd HH:mm:ss");
        return sdfNow.format(date);
    }
}
