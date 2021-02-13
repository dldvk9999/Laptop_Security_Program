package com.android.lsp_controller;

import android.util.Base64;

import java.math.BigInteger;
import java.nio.charset.StandardCharsets;
import java.security.InvalidAlgorithmParameterException;
import java.security.InvalidKeyException;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.spec.AlgorithmParameterSpec;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.IllegalBlockSizeException;
import javax.crypto.NoSuchPaddingException;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.SecretKeySpec;

class AES256Cipher {
    public static byte[] ivBytes = { 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00 };
    public static String secretKey = "738475CE202BCBA5EF11CF409C1ED7AD"; // '힘내 항상 난 NULL 응원해' -> MD5 해시 값
    public static String secretKey2 = "69af60e2fc6f580f3250eb0f7efb9612"; // 'LSP Controller Application' -> MD5 해시 값

    //AES256 암호화
    public static String AES_Encode(String str)    throws NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException, InvalidAlgorithmParameterException,    IllegalBlockSizeException, BadPaddingException {
        /*
        *
        *   AES_CBC_256 으로 블루투스 암호화 함.
        *   secretKey(개인키, MD5 해시된 값)에 시간값(밀리초)를 이어 붙여 다시 MD5 해시한 것을 메시지 암호화의 KEY로 삼음.
        *   클라이언트는 암호화한 메시지 값, 시간값(밀리초)을 secretKey로 암호화한 값 이렇게 두개를 보냄.
        *   => 암호화된 문자열(메시지 암호화)_시간값(밀리초)을 암호화한 문자열  이렇게 하나의 문자열로 만들어 전송함.
        *
        *   서버는 "_" 문자를 중심으로 2개로 나누어서 먼저 시간값을 secretKey로 복호화하고,
        *   secretKey를 MD5한 뒤 복호화한 시간값을 이어붙여 다시 MD5한 것을 메시지 복호화에 사용.
        *
        *   이러면 매번 같은 문자열을 보내도 항상 다르게 암호화가 되며, 모든 문자열을 암호화하여 보낼 수 있기에
        *   제 3자가 봐도 해독에 어려움이 있음.
        *
         */

        /* secretKey와 시간값을 이어 붙여 MD5 해시함 */
        long now = System.currentTimeMillis();
        String time = String.valueOf(now);
        String totalKey;
        totalKey = secretKey + time;
        totalKey = getMD5Hash(totalKey);

        /* 블루투스 전송 시 메시지 암호화 부분 */
        byte[] textBytes = str.getBytes(StandardCharsets.UTF_8);
        AlgorithmParameterSpec ivSpec = new IvParameterSpec(ivBytes);
        SecretKeySpec newKey = new SecretKeySpec(totalKey.getBytes(StandardCharsets.UTF_8), "AES");
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, newKey, ivSpec);

        /* 블루투스 전송시 시간값 암호화 부분 */
        byte[] textBytes2 = time.getBytes(StandardCharsets.UTF_8);
        AlgorithmParameterSpec ivSpec2 = new IvParameterSpec(ivBytes);
        SecretKeySpec timeKey = new SecretKeySpec(secretKey.getBytes(StandardCharsets.UTF_8), "AES");
        Cipher cipher2 = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher2.init(Cipher.ENCRYPT_MODE, timeKey, ivSpec2);

        /* 최종 암호화 부분 */
        String concat = Base64.encodeToString(cipher.doFinal(textBytes), 0) + "_" + Base64.encodeToString(cipher2.doFinal(textBytes2), 0);
        byte[] CipherMassage = concat.getBytes(StandardCharsets.UTF_8);
        AlgorithmParameterSpec ivSpec3 = new IvParameterSpec(ivBytes);
        SecretKeySpec cipherKey = new SecretKeySpec(secretKey2.getBytes(StandardCharsets.UTF_8), "AES");
        Cipher cipher3 = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher3.init(Cipher.ENCRYPT_MODE, cipherKey, ivSpec3);

        return Base64.encodeToString(cipher3.doFinal(CipherMassage), 0);
    }

    static String getMD5Hash(String text) {
        MessageDigest m;
        String hash =  null;

        try {
            m = MessageDigest.getInstance("MD5");
            m.update(text.getBytes(),0,text.length());
            hash = new BigInteger(1,m.digest()).toString(16);
        } catch(NoSuchAlgorithmException e){
            e.printStackTrace();
        }
        return hash;
    }
}
