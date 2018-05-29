package com.example.user.grpc_ssd;

import android.annotation.TargetApi;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.os.Build;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v7.app.AlertDialog;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import static android.Manifest.permission.CAMERA;
import static android.Manifest.permission.READ_EXTERNAL_STORAGE;
import static android.Manifest.permission.RECORD_AUDIO;
import static android.Manifest.permission.WRITE_EXTERNAL_STORAGE;

public class MainActivity extends AppCompatActivity {
    private Button connectBut;
    private EditText ip_edit;
    private EditText port_edit;
    private String ip;
    private String port;
    private boolean flag = true;
    private int language = 1;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        connectBut = (Button) findViewById(R.id.connectBut);

        ip_edit = (EditText) findViewById(R.id.ip_edit);
        port_edit = (EditText) findViewById(R.id.port_edit);

        // Activiy 실행 시 권한 체크
        if (checkPermission()) {
            requestPermissionAndContinue();
        }

        connectBut.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                ip = ip_edit.getText().toString();
                port = port_edit.getText().toString();
                if (ip.equals("") || port.equals("")) {
                    Toast.makeText(MainActivity.this, "IP와 PORT를 입력해 주세요", Toast.LENGTH_SHORT).show();
                    System.out.println(ip + " and " + port);
                } else {
                    Intent i = new Intent(MainActivity.this, ClientActivity.class);
                    System.out.println(ip + " and " + port);
                    i.putExtra("ip", ip);
                    i.putExtra("port", port);
                    i.putExtra("language", language);
                    startActivity(i);
                }
            }
        });
    }

    /**
     * 권한 체크
     */
    private static final int PERMISSION_REQUEST_CODE = 200;

    private boolean checkPermission() {

        return ContextCompat.checkSelfPermission(this, WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(this, READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(this, RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(MainActivity.this, CAMERA) != PackageManager.PERMISSION_GRANTED;
    }

    /**
     * 권한 요청
     */
    private void requestPermissionAndContinue() {
        if (ContextCompat.checkSelfPermission(this, WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(this, READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(this, RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(MainActivity.this, CAMERA) != PackageManager.PERMISSION_GRANTED) {

            if (ActivityCompat.shouldShowRequestPermissionRationale(this, WRITE_EXTERNAL_STORAGE)
                    && ActivityCompat.shouldShowRequestPermissionRationale(this, READ_EXTERNAL_STORAGE)
                    && ActivityCompat.shouldShowRequestPermissionRationale(this, RECORD_AUDIO)
                    && ActivityCompat.shouldShowRequestPermissionRationale(this, CAMERA)) {
                AlertDialog.Builder alertBuilder = new AlertDialog.Builder(this);
                alertBuilder.setCancelable(true);
                alertBuilder.setTitle("Permission Error");
                alertBuilder.setMessage("error");
                alertBuilder.setPositiveButton(android.R.string.yes, new DialogInterface.OnClickListener() {
                    @TargetApi(Build.VERSION_CODES.JELLY_BEAN)
                    public void onClick(DialogInterface dialog, int which) {
                        ActivityCompat.requestPermissions(MainActivity.this, new String[]{WRITE_EXTERNAL_STORAGE
                                , READ_EXTERNAL_STORAGE, RECORD_AUDIO, CAMERA}, PERMISSION_REQUEST_CODE);
                    }
                });
                AlertDialog alert = alertBuilder.create();
                alert.show();
                Log.e("", "permission denied, show dialog");
            } else {
                ActivityCompat.requestPermissions(MainActivity.this, new String[]{WRITE_EXTERNAL_STORAGE,
                        READ_EXTERNAL_STORAGE, RECORD_AUDIO, CAMERA}, PERMISSION_REQUEST_CODE);
            }
        }
    }

    /**
     * 메뉴 바 이벤트 처리
     * 언어 선택
     */
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.menu_client, menu);
        return true;
    }

    @Override
    public boolean onPrepareOptionsMenu(Menu menu) {
        if(flag) {
            menu.getItem(0).setChecked(true);
            menu.getItem(1).setChecked(false);
        } else {
            menu.getItem(0).setChecked(false);
            menu.getItem(1).setChecked(true);
        }


        return super.onPrepareOptionsMenu(menu);
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        int id = item.getItemId();

        switch (id) {
            case R.id.menu_eng:
                language = 1;
                flag = true;
                return true;
            case R.id.menu_kor:
                language = 2;
                flag = false;
                return true;
        }

        return super.onOptionsItemSelected(item);
    }
}
