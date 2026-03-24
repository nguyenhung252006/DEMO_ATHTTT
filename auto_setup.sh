#!/bin/bash

# 1. Cài GCC 32-bit nếu thiếu
if ! command -v gcc &> /dev/null || ! gcc -v 2>&1 | grep -q i686; then
    echo "[!] Cài GCC + multilib..."
    sudo apt update && sudo apt install build-essential gcc-multilib g++-multilib -y
else
    echo "[+] GCC đã sẵn sàng (32-bit support)"
fi

# 2. Tắt ASLR tạm thời (giúp debug địa chỉ cố định, nhưng exploit thật nên bật lại)
echo "[+] Tắt ASLR tạm thời..."
sudo sysctl -w kernel.randomize_va_space=0
# Để bật lại sau: sudo sysctl -w kernel.randomize_va_space=2

# 3. Biên dịch server với NX bật (giống môi trường thật, không -z execstack)
echo "[+] Biên dịch server (NX bật, stack protector tắt cho vuln buffer)"
gcc -fno-stack-protector -m32 -o server server.c
# Nếu muốn test shellcode cũ (không NX): thêm -z execstack
# gcc -fno-stack-protector -z execstack -m32 -o server server.c

# 4. Chạy server với nc (pipe để tương tác 2 chiều)
echo "[+] Chạy server trên port 4444 (dùng fifo cho bidirectional)..."
rm -f /tmp/f
mkfifo /tmp/f
cat /tmp/f | ./server 2>&1 | nc -lvnp 4444 > /tmp/f

# Bonus: Để debug dễ hơn, chạy trong gdb
# echo "[+] Debug mode: gdb --args ./server"
# gdb -q ./server
