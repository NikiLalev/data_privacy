pragma circom 2.0.0;

template MatrixMul(N) {
    // Assert maximum supported size
    assert(N <= 3);
    assert(N > 0);

    // Inputs: two N x N matrices
    signal input a[N][N];
    signal input b[N][N];

    // Output: resulting N x N matrix
    signal output out[N][N];

    // Intermediate signals to accumulate the dot products linearly
    // step[i][j][k] holds the sum of the first (k + 1) terms of the dot product
    signal step[N][N][N];

    for (var i = 0; i < N; i++) {
        for (var j = 0; j < N; j++) {
            // First product term for cell (i, j)
            step[i][j][0] <== a[i][0] * b[0][j];

            // Accumulate subsequent terms
            for (var k = 1; k < N; k++) {
                step[i][j][k] <== step[i][j][k - 1] + (a[i][k] * b[k][j]);
            }

            // Assign the completed sum to the output cell
            out[i][j] <== step[i][j][N - 1];
        }
    }
}

// Instantiate the component for a 3x3 matrix
component main = MatrixMul(3);