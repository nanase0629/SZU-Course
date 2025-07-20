#include <windows.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <omp.h> // Include the OpenMP header

#define blockSize 32 // 块大小，可以根据实际情况调整

void matrixMultiplyParallelBlocked(int size, float *a, float *b, float *c) {
    // 初始化c矩阵为0
    for (int i = 0; i < size; i++) {
        for (int j = 0; j < size; j++) {
            c[i * size + j] = 0;
        }
    }

    // 使用OpenMP进行并行计算
    #pragma omp parallel for collapse(2)
    for (int i = 0; i < size; i += blockSize) {
        for (int j = 0; j < size; j += blockSize) {
            for (int k = 0; k < size; k += blockSize) {
                for (int ii = i; ii < i + blockSize && ii < size; ii++) {
                    for (int jj = j; jj < j + blockSize && jj < size; jj++) {
                        double sum = 0;
                        for (int kk = k; kk < k + blockSize && kk < size; kk++) {
                            sum += a[ii * size + kk] * b[kk * size + jj];
                        }
                        c[ii * size + jj] += sum;
                    }
                }
            }
        }
    }
}

int main(int argc, char* argv[]) {
    float* a, * b, * c;
    long int i, j, k, size, m;
    LARGE_INTEGER frequency, start_time, end_time;

    if (argc < 2) {
        printf("\n\tUsage:%s <Row of square matrix>\n", argv[0]);
        exit(-1);
    }

    size = atoi(argv[1]);
    m = size * size;
    a = (float*)malloc(sizeof(float) * m);
    b = (float*)malloc(sizeof(float) * m);
    c = (float*)malloc(sizeof(float) * m);

    srand(time(NULL));

    // Initialize matrices a and b
    for (i = 0; i < size; i++) {
        for (j = 0; j < size; j++) {
            a[i * size + j] = (float)(rand() % 1000 / 100.0);
            b[j * size + i] = (float)(rand() % 1000 / 100.0);
        }
    }

    QueryPerformanceFrequency(&frequency);
    QueryPerformanceCounter(&start_time);

    // Parallelize the matrix multiplication using OpenMP with cache optimization
    #pragma omp parallel for private(i, k, j) shared(a, b, c)
    for(i=0;i<size;i++) { 
	    for(j=0;j<size;j++)  {
            c[i*size+j] = 0; 
            for (k=0;k<size;k++) 
                c[i*size+j] += a[i*size+k]*b[j*size+k];
        }
    }
    
  	/*for(i=0;i<size;i++) { 
        for(j=0;j<size;j++)  {
            c[i*size+j] = 0; 
            for (k=0;k<size;k++) 
                c[i*size+j] += a[i*size+k]*b[j*size+k];
        }
    }*/
   
    //matrixMultiplyParallelBlocked(size,a,b,c);

    QueryPerformanceCounter(&end_time);

    double elapsed_time = (double)(end_time.QuadPart - start_time.QuadPart) / frequency.QuadPart;
    printf("Execution time = %.6f seconds\n", elapsed_time);

    free(a);
    free(b);
    free(c);

    return 0;
}

