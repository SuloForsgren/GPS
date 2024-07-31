#include <stdlib.h>
#include <stdio.h>
#include <string.h>

//Function for opening the cams.csv file
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
    return;
}

int main(void) {
    const char *file_path = "/home/sulof/GPS/CamLocation/cams.csv";
    openFile(file_path)
    return 0;
}

