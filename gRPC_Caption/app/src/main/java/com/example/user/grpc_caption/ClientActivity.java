package com.example.user.grpc_caption;

import android.annotation.TargetApi;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.media.MediaPlayer;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
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
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.google.common.primitives.Bytes;
import com.google.protobuf.ByteString;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.stub.StreamObserver;
import io.grpctest.imageCaptioning.ImageCaptionServiceGrpc;
import io.grpctest.imageCaptioning.Request;
import io.grpctest.imageCaptioning.Response;

import static android.Manifest.permission.CAMERA;
import static android.Manifest.permission.READ_EXTERNAL_STORAGE;
import static android.Manifest.permission.RECORD_AUDIO;
import static android.Manifest.permission.WRITE_EXTERNAL_STORAGE;

public class ClientActivity extends AppCompatActivity {

    private static String ip = "Server IP";
    private static int port = 1111; // port 번호
    private static List<String> audio_id = Arrays.asList("1");
    private static final int PICK_FROM_ALBUM = 0;
    private static final int PICK_FROM_CAMERA = 1;
    private static final int PICK_FROM_CAMERA2 = 2;
    private boolean flag = true;  // Menu Flag

    private static Bitmap photo = null;
    private ImageView iv_UserPhoto;
    private Button btn_SelectPicture;
    private Button btn_Upload;

    private static TextView resultText;
    private static String[] resultStr = new String[1];

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_client);

        iv_UserPhoto = (ImageView) this.findViewById(R.id.user_image);
        btn_SelectPicture = (Button) this.findViewById(R.id.btn_SelectPicture);
        btn_Upload = (Button) this.findViewById(R.id.btn_Upload);
        resultText = (TextView) this.findViewById(R.id.resultText);

        ip = getIntent().getStringExtra("ip");
        port = Integer.parseInt(getIntent().getStringExtra("port"));
        System.out.println(ip + " and " +port);

        // Activiy 실행 시 권한 체크
        if (checkPermission()) {
            requestPermissionAndContinue();
        }

        btn_SelectPicture.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resultText.setText("");
                SelectPicture();
            }
        });

        btn_Upload.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                resultText.setText("");
                if (photo == null) {
                    Toast.makeText(ClientActivity.this, "사진을 선택해 주세요", Toast.LENGTH_SHORT).show();
                } else {
                    new GrpcTask().execute();
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
                && ContextCompat.checkSelfPermission(ClientActivity.this, CAMERA) != PackageManager.PERMISSION_GRANTED;
    }

    /**
     * 권한 요청
     */
    private void requestPermissionAndContinue() {
        if (ContextCompat.checkSelfPermission(this, WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(this, READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(this, RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED
                && ContextCompat.checkSelfPermission(ClientActivity.this, CAMERA) != PackageManager.PERMISSION_GRANTED) {

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
                        ActivityCompat.requestPermissions(ClientActivity.this, new String[]{WRITE_EXTERNAL_STORAGE
                                , READ_EXTERNAL_STORAGE, RECORD_AUDIO, CAMERA}, PERMISSION_REQUEST_CODE);
                    }
                });
                AlertDialog alert = alertBuilder.create();
                alert.show();
                Log.e("", "permission denied, show dialog");
            } else {
                ActivityCompat.requestPermissions(ClientActivity.this, new String[]{WRITE_EXTERNAL_STORAGE,
                        READ_EXTERNAL_STORAGE, RECORD_AUDIO, CAMERA}, PERMISSION_REQUEST_CODE);
            }
        }
    }

    /**
     * 카메라앱을 통한 사진 촬영
     */
    public void doTakePhotoAction() {
        Intent intent = new Intent();
        intent.setAction(MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(intent, PICK_FROM_CAMERA);

    }

    /**
     * 앨범에서 이미지 로드
     */
    public void doTakeAlbumAction() {
        Intent intent = new Intent(Intent.ACTION_PICK);
        intent.setType(android.provider.MediaStore.Images.Media.CONTENT_TYPE);
        intent.setData(android.provider.MediaStore.Images.Media.EXTERNAL_CONTENT_URI);
        startActivityForResult(intent, PICK_FROM_ALBUM);
    }

    /**
     * 이미지 작업
     */
    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode,resultCode,data);
        if(resultCode != RESULT_OK)
            return;

        switch(requestCode)
        {
            case PICK_FROM_CAMERA: {
                final Bundle extras = data.getExtras();

                if(extras != null) {
                    photo = (Bitmap)data.getExtras().get("data");
                    iv_UserPhoto.setImageBitmap(photo);
                    break;
                }

                break;
            }
            case PICK_FROM_ALBUM: {
                try {
                    photo = MediaStore.Images.Media.getBitmap(getContentResolver(), data.getData());
                    iv_UserPhoto.setImageBitmap(photo);
                    break;
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
            case PICK_FROM_CAMERA2: {
                Intent i = getIntent();
                Bundle b = i.getExtras();
                photo = (Bitmap) b.get("data");
                iv_UserPhoto.setImageBitmap(photo);
                break;
            }
        }
    }

    /**
     * Audio 실행
     */
    public static void autio_start(byte[] bytes) {
        // 임시 파일 생성 후 삭제
        String outputFile= Environment.getExternalStorageDirectory().getAbsolutePath() + "/tts.mp3";
        File path = new File(outputFile);
        FileOutputStream fos = null;
        try {
            fos = new FileOutputStream(path);
            fos.write(bytes);
            fos.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
        MediaPlayer mediaPlayer = new MediaPlayer();

        try {
            mediaPlayer.setDataSource(outputFile);

            mediaPlayer.prepare();
            mediaPlayer.start();
        } catch (IOException e) {
            e.printStackTrace();
        }

        path.delete();
    }

    /**
     * 다이얼 로그 출력
     */
    public void SelectPicture() {
        DialogInterface.OnClickListener camaeraListener = new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                //Intent i = new Intent(ClientActivity.this, CameraActivity.class);
                //startActivity(i);
                doTakePhotoAction();
            }
        };
        DialogInterface.OnClickListener albumListener = new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                doTakeAlbumAction();
            }
        };

        DialogInterface.OnClickListener cancelListener = new DialogInterface.OnClickListener() {
            @Override
            public void onClick(DialogInterface dialog, int which) {
                dialog.dismiss();
            }
        };

        new AlertDialog.Builder(this)
                .setTitle("업로드할 이미지 선택")
                .setPositiveButton("사진촬영", camaeraListener)
                .setNeutralButton("앨범선택", albumListener)
                .setNegativeButton("취소", cancelListener)
                .show();
    }

    /**
     * AsyncTask 동작
     * ArrayList로 return
     */
    private class GrpcTask extends AsyncTask<Void, Void, List<Byte>> {
        private ManagedChannel channel;
        private Throwable failed;

        @Override
        protected void onPreExecute() {
            super.onPreExecute();
            Toast.makeText(ClientActivity.this, "Loading..", Toast.LENGTH_SHORT).show();
        }

        @Override
        protected List<Byte> doInBackground(Void... nothing) {
            try {
                final List<Byte> byteList = new ArrayList<>();
                channel = ManagedChannelBuilder.forAddress(ip, port).usePlaintext(true).build();
                ImageCaptionServiceGrpc.ImageCaptionServiceStub stub = ImageCaptionServiceGrpc.newStub(channel);
                final CountDownLatch finishLatch = new CountDownLatch(1);

                // 비트맵 -> byteArray -> ByteString로 변환
                ByteArrayOutputStream stream = new ByteArrayOutputStream();
                photo.compress(Bitmap.CompressFormat.JPEG, 100, stream);
                byte[] b = stream.toByteArray();
                ByteString bs = ByteString.copyFrom(b);

                long start = System.currentTimeMillis();

                StreamObserver<Response> responseObserver = new StreamObserver<Response>() {
                    @Override
                    public void onNext(Response response) {
                        resultStr[0] = response.getResultText();
                        for (int i = 0; i < response.getAudioData().toByteArray().length; i++) {
                            // 서버로 부터 받은 데이터 ArrayList에 추가
                            byteList.add(response.getAudioData().toByteArray()[i]);
                        }
                    }

                    @Override
                    public void onError(Throwable t) {
                        failed = t;
                        finishLatch.countDown();
                        System.out.println("onError() 호출");
                    }

                    @Override
                    public void onCompleted() {
                        System.out.println("서버로부터 응답 성공");
                        finishLatch.countDown();
                    }
                };

                StreamObserver<Request> requestObserver = stub.dataStreaming(responseObserver);
                try {
                    //서버에 데이터 전송
                    requestObserver.onNext(Request.newBuilder().setImageData(bs).build());
                    for (String id: audio_id) {
                        requestObserver.onNext(Request.newBuilder().setAudioId(id).build());
                    }
                } catch (RuntimeException e) {
                    requestObserver.onError(e);
                    throw e;
                }

                requestObserver.onCompleted();

                if(!finishLatch.await(1, TimeUnit.MINUTES)) {
                    throw new RuntimeException("Could not finish rpc within 1 minute, the server is likely down");
                }

                if(failed != null) {
                    throw new RuntimeException(failed);
                }
                long end = System.currentTimeMillis();
                System.out.println(end - start);
                return byteList;
            } catch (Exception e) {
                StringWriter sw = new StringWriter();
                PrintWriter pw = new PrintWriter(sw);
                e.printStackTrace(pw);
                pw.flush();
                return null;
            }
        }

        @Override
        protected void onProgressUpdate(Void... values) {
            super.onProgressUpdate(values);
        }

        @Override
        protected void onPostExecute(List<Byte> result) {
            channel.shutdown();
            // ArrayList -> byte로 변환
            byte[] bytes = Bytes.toArray(result);
            resultText.setText(resultStr[0]);
            // gTTS 실행
            autio_start(bytes);
        }
    }

    /**
     * 메뉴 바 이벤트 처리
     * TTS 엔진 선택
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
            case R.id.menu_gtts:
                audio_id = Arrays.asList("1");
                flag = true;
                return true;
            case R.id.menu_stts:
                audio_id = Arrays.asList("2");
                flag = false;
                return true;
        }

        return super.onOptionsItemSelected(item);
    }
}
