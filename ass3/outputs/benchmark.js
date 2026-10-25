const snarkjs = require("snarkjs");
const fs = require("node:fs");
const { performance } = require("node:perf_hooks");

const zkey = "matrix_mult_final.zkey";
const witness = "witness.wtns";
const vKey = JSON.parse(fs.readFileSync("verification_key.json", "utf8"));

function median(values) {
    const sorted = [...values].sort((a, b) => a - b);
    return sorted[Math.floor(sorted.length / 2)];
}

async function main() {
    // Warm up before collecting samples.
    let result = await snarkjs.groth16.prove(zkey, witness);
    await snarkjs.groth16.verify(vKey, result.publicSignals, result.proof);

    const proveTimes = [];
    for (let i = 0; i < 100; i++) {
        const start = performance.now();
        result = await snarkjs.groth16.prove(zkey, witness);
        proveTimes.push(performance.now() - start);
    }

    const verifyTimes = [];
    for (let i = 0; i < 100; i++) {
        const start = performance.now();
        const valid = await snarkjs.groth16.verify(
            vKey,
            result.publicSignals,
            result.proof
        );
        verifyTimes.push(performance.now() - start);
        if (!valid) throw new Error("Proof verification failed");
    }

    console.log(`Median proving time: ${median(proveTimes).toFixed(2)} ms`);
    console.log(`Median verification time: ${median(verifyTimes).toFixed(2)} ms`);
}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});