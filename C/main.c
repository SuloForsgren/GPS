#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <termios.h>

// Function to open and configure the serial port
int open_serial_port(const char *device) {
    int serial_port = open(device, O_RDWR | O_NOCTTY | O_NDELAY);

    if (serial_port == -1) {
        perror("open_serial_port: Unable to open serial port");
        return -1;
    }

    struct termios options;
    tcgetattr(serial_port, &options);

    // Set baud rates to 9600
    cfsetispeed(&options, B9600);
    cfsetospeed(&options, B9600);

    // Configure the port to use 8 data bits, no parity, and 1 stop bit
    options.c_cflag &= ~PARENB; // No parity
    options.c_cflag &= ~CSTOPB; // 1 stop bit
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8; // 8 data bits

    // Enable the receiver and set local mode
    options.c_cflag |= (CLOCAL | CREAD);

    // Set the new options for the port
    tcsetattr(serial_port, TCSANOW, &options);

    return serial_port;
}

// Function to close the serial port
void close_serial_port(int serial_port) {
    close(serial_port);
}

// Function to read data from the serial port
int read_from_serial_port(int serial_port, char *buffer, size_t size) {
    return read(serial_port, buffer, size);
}

// Function for opening the cams.csv file and printing its contents
void openFile(const char *file_path) {
    FILE *file = fopen(file_path, "r");
    char buffer[100];

    if (file == NULL) {
        printf("Failed to open file.\n");
        return;
    }

    while (fgets(buffer, sizeof(buffer), file)) {
        // Remove newline character if present
        buffer[strcspn(buffer, "\n")] = 0;

        // Tokenize the line by commas
        char *token = strtok(buffer, ",");
        if (token != NULL) {
            // Print the 1st column
            printf("Longitude: %s\n", token);

            // Fetch and print the 2nd column
            token = strtok(NULL, ",");
            if (token != NULL) {
                printf("Latitude: %s\n", token);
            } else {
                printf("No coords found\n");
            }
        } else {
            printf("No columns available\n");
        }
    }

    fclose(file);
}

int main(void) {
    const char *serial_device = "/dev/serial0";
    int serial_port = open_serial_port(serial_device);

    if (serial_port == -1) {
        return 1;
    }

    char buffer[256];
    int bytes_read;

    while (1) {
        bytes_read = read_from_serial_port(serial_port, buffer, sizeof(buffer) - 1);

	   //If bytes read from serial then print data else print error --> sleep for 100ms
        if (bytes_read > 0) {
            buffer[bytes_read] = '\0'; // Null-terminate the string
            printf("Read %d bytes: %s\n", bytes_read, buffer);
        } else if (bytes_read < 0) {
            perror("Error reading from serial port");
        }

        usleep(100000); // Sleep for 100ms
    }

    close_serial_port(serial_port);
    return 0;
}
