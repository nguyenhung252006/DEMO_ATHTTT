#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <stdlib.h>

void vulnerable_function() {
    char buffer[64];

    // Xóa sạch bộ đệm (tốt)
    memset(buffer, 0, sizeof(buffer));

    printf("--- HE THONG DANG DOI PAYLOAD ---\n");
    printf("Nhap du lieu (toi da 64 ky tu): ");

    fflush(stdout);  // Ép flush ngay (đã có, tốt)

    /* LỖI Ở ĐÂY: buffer[64] nhưng đọc 256 byte → overflow */
    read(0, buffer, 256);

    // Thêm dòng này để dễ debug: in ra địa chỉ buffer (giúp xác nhận offset khi dùng gdb)
    printf("[DEBUG] Dia chi buffer: %p\n", (void *)buffer);

    printf("Du lieu da nhan xong. Dang kiem tra stack...\n");
    fflush(stdout);

    // Thêm sleep ngắn để nc có thời gian interact trước khi chương trình exit
    sleep(1);  // Optional: cho phép shell tương tác nếu exploit thành công
}

int main() {
    // Tắt buffering stdout hoàn toàn → output hiện ngay qua nc (đã có, tốt)
    setvbuf(stdout, NULL, _IONBF, 0);

    // Optional: tắt buffering stdin nếu cần, nhưng thường không cần
    // setvbuf(stdin, NULL, _IONBF, 0);

    vulnerable_function();

    printf("Chuong trinh ket thuc binh thuong (Khong bi hack).\n");
    return 0;
}
