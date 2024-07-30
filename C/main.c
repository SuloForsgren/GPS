#include <stdlib.h>
#include <stdio.h>

void openFile(const char *file_path) {
	FILE *file = fopen(file_path, "r");
	char buffer[100];
	if (file == NULL) {
		printf("Perkeleen virhe >:(");
	}
	else {
		while (fgets(buffer, sizeof(buffer), file)) {
			 buffer[strcspn(buffer, "\n")] = 0;
			 
			 char *token = strtok(buffer, ",");
			 if (token != NULL) {
				    printf("%s\n", token);
				    token = strtok(NULL, ",");
				    if (token != NULL) {
						  printf("%s\n", token);
				    }
				    else {
						  printf("No 2nd column!\n");
				    }
			 else {
				    printf("No columns available\n");
		}
	}
	fclose(file);
}

int main(void) {
	const char *file_path = "/home/sulof/GPS/CamLocation/cams.csv";
	openFile(file_path);
	return 0;
}
