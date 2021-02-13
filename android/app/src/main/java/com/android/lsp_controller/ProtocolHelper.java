package com.android.lsp_controller;

class ProtocolHelper {

    static byte[] joinBytesArrays(byte[][] bytes) {
        int total_length = 0;

        for(byte[] bs : bytes) {
            total_length += bs.length;
        }

        byte[] joined_bytes = new byte[total_length];
        int i = 0;
        for(byte[] bs : bytes) {
            for(byte b : bs) {
                joined_bytes[i++] = b;
            }
        }

        return joined_bytes;
    }

}
