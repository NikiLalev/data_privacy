// SPDX-License-Identifier: GPL-3.0
/*
    Copyright 2021 0KIMS association.

    This file is generated with [snarkJS](https://github.com/iden3/snarkjs).

    snarkJS is a free software: you can redistribute it and/or modify it
    under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    snarkJS is distributed in the hope that it will be useful, but WITHOUT
    ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
    or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
    License for more details.

    You should have received a copy of the GNU General Public License
    along with snarkJS. If not, see <https://www.gnu.org/licenses/>.
*/

pragma solidity >=0.7.0 <0.9.0;

contract Groth16Verifier {
    // Scalar field size
    uint256 constant r    = 21888242871839275222246405745257275088548364400416034343698204186575808495617;
    // Base field size
    uint256 constant q   = 21888242871839275222246405745257275088696311157297823662689037894645226208583;

    // Verification Key data
    uint256 constant alphax  = 21239420834836819628187426391807758271608318943265445223945713617769063942604;
    uint256 constant alphay  = 17856208580937730119667167678517687531843041088946426711090344150508761904416;
    uint256 constant betax1  = 2630924499592560678005643826077706120538014811044927582647517151775511194811;
    uint256 constant betax2  = 20955621089682800069328157705914954108229780409477434426130870809757238351566;
    uint256 constant betay1  = 9930329433280419886204581282986876875090717635064061214326040710788510590808;
    uint256 constant betay2  = 18483057679054987451801379091487547547918421111005088928389204824640834884799;
    uint256 constant gammax1 = 11559732032986387107991004021392285783925812861821192530917403151452391805634;
    uint256 constant gammax2 = 10857046999023057135944570762232829481370756359578518086990519993285655852781;
    uint256 constant gammay1 = 4082367875863433681332203403145435568316851327593401208105741076214120093531;
    uint256 constant gammay2 = 8495653923123431417604973247489272438418190587263600148770280649306958101930;
    uint256 constant deltax1 = 9142751346322250773134986108175126825200690959984754971356581702671939832595;
    uint256 constant deltax2 = 20715943201056614889743908247778810831560214402939692828217218344168473608824;
    uint256 constant deltay1 = 8765915941353603709153286685377324258249779552939352263757277451078906383888;
    uint256 constant deltay2 = 10569730666206140723768764308747781966234407772234925348683291567095089106408;

    
    uint256 constant IC0x = 17188684433409418474360704586502031138569207535624429194324417734215888640957;
    uint256 constant IC0y = 19668234901413172815217750087293393657978120873561425667395010433902982319516;
    
    uint256 constant IC1x = 5191200923857520750471972705742118215406199865497965973665903958209961405709;
    uint256 constant IC1y = 11997017270514491750741465601304027324675213248006879119698338799902848823162;
    
    uint256 constant IC2x = 11198430731757129419189094907862292339768004580759888810446348349082174843227;
    uint256 constant IC2y = 19493804885979537339095346139879438481724670633935835466833831325468689639589;
    
    uint256 constant IC3x = 8325446376357281319845999022896029391149652995615881004524992741125248263134;
    uint256 constant IC3y = 18157360778456342876937563319843606467107751721774347902688252208787177847263;
    
    uint256 constant IC4x = 3796296562703024121546293451578466128333018276234668351168424027989111572743;
    uint256 constant IC4y = 17466473364707111961222601462639489851244075737185199642970810009515497442849;
    
    uint256 constant IC5x = 2135344822781711118093141111012626538305063979251035050322320379867920987516;
    uint256 constant IC5y = 15015016799081692139761907752808336374498648141772194790614616259174059333479;
    
    uint256 constant IC6x = 18763374833757718564047530924929174854467860140537124427953201633157460346101;
    uint256 constant IC6y = 1579267600053889509184185058768356208170641119099985892512819250531931122707;
    
    uint256 constant IC7x = 7157091929786295952886978338193163151765747623242645921620027477706261188959;
    uint256 constant IC7y = 8459750679110071125298372686333107663522048458613968278329927595814548507994;
    
    uint256 constant IC8x = 2305841930615562833995210417670864190646620199134475770916030422131666194071;
    uint256 constant IC8y = 13596101417720517011883785156741198722345755311478435456355925233877768955490;
    
    uint256 constant IC9x = 304688294231828807553642061097852785561132666626916175814779617314454773312;
    uint256 constant IC9y = 2526475162694926078232875234974485312500992979871970942607833626889346202860;
    
 
    // Memory data
    uint16 constant pVk = 0;
    uint16 constant pPairing = 128;

    uint16 constant pLastMem = 896;

    function verifyProof(uint[2] calldata _pA, uint[2][2] calldata _pB, uint[2] calldata _pC, uint[9] calldata _pubSignals) public view returns (bool) {
        assembly {
            function checkField(v) {
                if iszero(lt(v, r)) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }
            
            // G1 function to multiply a G1 value(x,y) to value in an address
            function g1_mulAccC(pR, x, y, s) {
                let success
                let mIn := mload(0x40)
                mstore(mIn, x)
                mstore(add(mIn, 32), y)
                mstore(add(mIn, 64), s)

                success := staticcall(sub(gas(), 2000), 7, mIn, 96, mIn, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }

                mstore(add(mIn, 64), mload(pR))
                mstore(add(mIn, 96), mload(add(pR, 32)))

                success := staticcall(sub(gas(), 2000), 6, mIn, 128, pR, 64)

                if iszero(success) {
                    mstore(0, 0)
                    return(0, 0x20)
                }
            }

            function checkPairing(pA, pB, pC, pubSignals, pMem) -> isOk {
                let _pPairing := add(pMem, pPairing)
                let _pVk := add(pMem, pVk)

                mstore(_pVk, IC0x)
                mstore(add(_pVk, 32), IC0y)

                // Compute the linear combination vk_x
                
                g1_mulAccC(_pVk, IC1x, IC1y, calldataload(add(pubSignals, 0)))
                
                g1_mulAccC(_pVk, IC2x, IC2y, calldataload(add(pubSignals, 32)))
                
                g1_mulAccC(_pVk, IC3x, IC3y, calldataload(add(pubSignals, 64)))
                
                g1_mulAccC(_pVk, IC4x, IC4y, calldataload(add(pubSignals, 96)))
                
                g1_mulAccC(_pVk, IC5x, IC5y, calldataload(add(pubSignals, 128)))
                
                g1_mulAccC(_pVk, IC6x, IC6y, calldataload(add(pubSignals, 160)))
                
                g1_mulAccC(_pVk, IC7x, IC7y, calldataload(add(pubSignals, 192)))
                
                g1_mulAccC(_pVk, IC8x, IC8y, calldataload(add(pubSignals, 224)))
                
                g1_mulAccC(_pVk, IC9x, IC9y, calldataload(add(pubSignals, 256)))
                

                // -A
                mstore(_pPairing, calldataload(pA))
                mstore(add(_pPairing, 32), mod(sub(q, calldataload(add(pA, 32))), q))

                // B
                mstore(add(_pPairing, 64), calldataload(pB))
                mstore(add(_pPairing, 96), calldataload(add(pB, 32)))
                mstore(add(_pPairing, 128), calldataload(add(pB, 64)))
                mstore(add(_pPairing, 160), calldataload(add(pB, 96)))

                // alpha1
                mstore(add(_pPairing, 192), alphax)
                mstore(add(_pPairing, 224), alphay)

                // beta2
                mstore(add(_pPairing, 256), betax1)
                mstore(add(_pPairing, 288), betax2)
                mstore(add(_pPairing, 320), betay1)
                mstore(add(_pPairing, 352), betay2)

                // vk_x
                mstore(add(_pPairing, 384), mload(add(pMem, pVk)))
                mstore(add(_pPairing, 416), mload(add(pMem, add(pVk, 32))))


                // gamma2
                mstore(add(_pPairing, 448), gammax1)
                mstore(add(_pPairing, 480), gammax2)
                mstore(add(_pPairing, 512), gammay1)
                mstore(add(_pPairing, 544), gammay2)

                // C
                mstore(add(_pPairing, 576), calldataload(pC))
                mstore(add(_pPairing, 608), calldataload(add(pC, 32)))

                // delta2
                mstore(add(_pPairing, 640), deltax1)
                mstore(add(_pPairing, 672), deltax2)
                mstore(add(_pPairing, 704), deltay1)
                mstore(add(_pPairing, 736), deltay2)


                let success := staticcall(sub(gas(), 2000), 8, _pPairing, 768, _pPairing, 0x20)

                isOk := and(success, mload(_pPairing))
            }

            let pMem := mload(0x40)
            mstore(0x40, add(pMem, pLastMem))

            // Validate that all evaluations ∈ F
            
            checkField(calldataload(add(_pubSignals, 0)))
            
            checkField(calldataload(add(_pubSignals, 32)))
            
            checkField(calldataload(add(_pubSignals, 64)))
            
            checkField(calldataload(add(_pubSignals, 96)))
            
            checkField(calldataload(add(_pubSignals, 128)))
            
            checkField(calldataload(add(_pubSignals, 160)))
            
            checkField(calldataload(add(_pubSignals, 192)))
            
            checkField(calldataload(add(_pubSignals, 224)))
            
            checkField(calldataload(add(_pubSignals, 256)))
            

            // Validate all evaluations
            let isValid := checkPairing(_pA, _pB, _pC, _pubSignals, pMem)

            mstore(0, isValid)
             return(0, 0x20)
         }
     }
 }
