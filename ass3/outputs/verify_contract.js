const fs = require("node:fs");
const { execSync } = require("node:child_process");

process.chdir(__dirname);
module.paths.push(execSync("npm root -g", { encoding: "utf8" }).trim());

const snarkjs = require("snarkjs");
const solc = require("solc");
const { ethers } = require("ethers");
const { createVM } = require("@ethereumjs/vm");
const { hexToBytes } = require("@ethereumjs/util");

async function main() {
    const input = {
        language: "Solidity",
        sources: { "verifier.sol": { content: fs.readFileSync("verifier.sol", "utf8") } },
        settings: { outputSelection: { "*": { "*": ["abi", "evm.bytecode.object"] } } }
    };
    const compiled = JSON.parse(solc.compile(JSON.stringify(input)));
    const contract = compiled.contracts["verifier.sol"]["Groth16Verifier"];
    const iface = new ethers.Interface(contract.abi);

    // local EVM
    const vm = await createVM();
    const deploy = await vm.evm.runCall({ data: hexToBytes("0x" + contract.evm.bytecode.object) });
    const contractAddr = deploy.createdAddress;
    // define function to call the contract
    async function verifyOnChain(a, b, c, pub) {
        const data = iface.encodeFunctionData("verifyProof", [a, b, c, pub]);
        const res = await vm.evm.runCall({ to: contractAddr, data: hexToBytes(data) });
        return iface.decodeFunctionResult("verifyProof", res.execResult.returnValue)[0];
    }

    const proof = JSON.parse(fs.readFileSync("proof.json", "utf8"));
    const publicSignals = JSON.parse(fs.readFileSync("public.json", "utf8"));
    const rawCallData = await snarkjs.groth16.exportSolidityCallData(proof, publicSignals);
    const [pA, pB, pC, pubSignals] = JSON.parse(`[${rawCallData}]`);

    // test differnt scenarios
    console.log("Valid proof & public output:", await verifyOnChain(pA, pB, pC, pubSignals));

    const wrongPub = [...pubSignals];
    wrongPub[0] = "0x0000000000000000000000000000000000000000000000000000000000000099";
    console.log("Tampered public output C[0,0]:", await verifyOnChain(pA, pB, pC, wrongPub));

    const wrongPA = [pA[1], pA[0]];
    console.log("Tampered proof point _pA:", await verifyOnChain(wrongPA, pB, pC, pubSignals));
    process.exit(0);
}

main();
