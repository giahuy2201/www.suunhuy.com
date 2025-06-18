import serial
import time
import os,sys

# take 128*1024^2/(2048+64)*1.6/3600/24 = 4.5 days to dump the chip

MAIN_START = b'dump (2048):'
OOB_START = b'OOB (64):'
OOB_LEN = 196
SPACE_CHARS = b"\x20\x0A\x09\x0D" # space \n \t \r

BLOCK_SIZE = 2048  # Adjust to match the NAND dump size per block
BUFFER_SIZE = 6500

def clean(data):
    return bytes(b for b in data if b not in SPACE_CHARS)

def convert(data):
    # binary = bytes.fromhex(data.decode())
    try:
        binary = bytes.fromhex(data.decode())
    except ValueError as e:
        print(data)
        print(f"Error: {e}")
    return binary

def parse(data):
    s1 = data.find(MAIN_START)
    s2 = data.find(OOB_START)
    s3 = s2+len(OOB_START)+OOB_LEN
    if s1 == -1 or s2 == -1 or s3 == -1:
        print('Snippet not found ',s1,s2,s3)
        sys.exit(1)
    main = convert(clean(data[s1+len(MAIN_START):s2]))
    oob = convert(clean(data[s2+len(OOB_START):s3]))
    return main, oob


def main():
    serial_path = sys.argv[1]
    baud_rate = 115200  # Set the baud rate (adjust if needed)
    
    # Open the serial device
    try:
        ser = serial.Serial(serial_path, baudrate=baud_rate, timeout=1)
        print(f"Opened serial device {serial_path} at {baud_rate} baud.")
    except Exception as e:
        print(f"Failed to open serial device: {e}")
        return

    if len(sys.argv) > 2:
        address = int(sys.argv[2],16)
    else:
        address = 0
    # Open a binary file to save the output
    output_file = f"dump-{hex(address)}.bin"
    try:
        with open(output_file, "wb") as f:

            while True:
                # if address > 4096:
                #     break
                # Build and send the `nand dump` command
                command = f"nand dump {hex(address)}\n"
                print(f"Sending command: {command.strip()}")
                ser.write(command.encode())
                start_time = time.perf_counter()
                time.sleep(0.5)  # Wait for the device to process the command
                # Read the output from the serial device
                data = ser.read(BUFFER_SIZE)
                
                if not data:
                    print("No more data received. Exiting.")
                    break
                elif len(data) < 50:
                    print(str(data))
                    break
                main,oob = parse(data)
                # Save the received data to the binary file
                f.write(main+oob)
                runtime = time.perf_counter() - start_time
                print(f"Saved {len(data)} bytes from address {address} in {runtime:.4f} seconds.")

                # Increment the address for the next block
                address += BLOCK_SIZE

        print(f"NAND dump saved to {output_file}.")
    except Exception as e:
        print(f"Error during file writing: {e}")
    finally:
        ser.close()
        print("Serial device closed.")

if __name__ == "__main__":
    main()
