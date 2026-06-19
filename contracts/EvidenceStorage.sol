// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EvidenceStorage {
    struct Evidence {
        string caseId;
        string evidenceId;
        string cid;
        uint256 timestamp;
        address uploader;
    }

    Evidence[] public allEvidence;
    mapping(string => Evidence) public evidenceMap;
    mapping(string => bool) public exists;

    event EvidenceStored(string evidenceId, string caseId, string cid, address uploader);

    function storeEvidence(string memory caseId, string memory evidenceId, string memory cid) external {
        require(!exists[evidenceId], "Evidence already stored");
        Evidence memory newEvidence = Evidence(caseId, evidenceId, cid, block.timestamp, msg.sender);
        allEvidence.push(newEvidence);
        evidenceMap[evidenceId] = newEvidence;
        exists[evidenceId] = true;
        emit EvidenceStored(evidenceId, caseId, cid, msg.sender);
    }

    function getEvidence(string memory evidenceId) external view returns (string memory, string memory, string memory, uint256, address) {
        Evidence memory e = evidenceMap[evidenceId];
        return (e.caseId, e.evidenceId, e.cid, e.timestamp, e.uploader);
    }

    function getCount() external view returns (uint) {
        return allEvidence.length;
    }
}