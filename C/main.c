#include <stdlib.h>
#include <stdio.h>

void openFile(file_path) {
	FILE *file = fopen(file_path, "r");
	char buffer[100];
	if (file == NULL) {
		printf("Perkeleen virhe >:(");
	}
	else {
		while (fgets(buffer, sizeof(buffer), file)) {
			printf("%s", buffer);
		}
	}
	fclose(file);
}

int main(void) {
	char file_path = "/home/sulof/GPS/CamLocation/cams.csv";
	openFile(file_path);
	return 0;
}
