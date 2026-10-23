pragma circom 2.0.0;

template SumProduct() {

    // Declaration
    signal input a;
    signal input b;

    signal output sum;
    signal output product;

    // Constraints & Assignments
    sum <== a + b;
    product <== a * b;
}

component main = SumProduct();