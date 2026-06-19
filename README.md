Cyber Evidence Integrity and Incident Reporting System Using 
Blockchain 
1. Introduction 
1.1 Background 
Cybercrime has become one of the most significant threats to individuals, organizations, and governments worldwide. As digital incidents increase in frequency and complexity, the need for secure, transparent, and trustworthy incident reporting and evidence management systems has never been greater. Traditional centralized systems suffer from vulnerabilities such as insider threats, data tampering, lack of transparency, and weak chain-of-custody tracking. These weaknesses undermine the integrity of digital investigations and erode public trust in forensic processes. 
1.2 Problem Statement 
Current cyber incident reporting and evidence management platforms typically rely on centralized databases, which present several critical challenges: 
•	Insider Threats: Investigators or administrators with malicious intent can delete, modify, or conceal evidence. 
•	Lack of Transparency: Victims have limited visibility into the progress of their cases and the handling of their evidence. 
•	Weak Chain of Custody: Evidence interactions are often poorly documented, making it difficult to prove authenticity in legal proceedings. 
•	Centralized Control: A single point of failure exists where a corrupt administrator could manipulate the entire system. 
•	Inadequate Integrity Guarantees: Without cryptographic verification, evidence integrity cannot be independently verified. 
1.3 Objectives 
The primary objective of this project is to design, develop, and evaluate a Cyber Evidence Integrity and Incident Reporting System (CEIRS) that leverages blockchain technology to address the aforementioned challenges. Specific objectives include: 
•	Enable secure cyber incident reporting by victims. 
•	Support uploading of multiple evidence formats with automatic encryption and hashing. 
•	Maintain an immutable, auditable record of all evidence and case actions. 
•	Implement a multi-role governance system to prevent abuse of authority. 
•	Provide full chain-of-custody tracking for all evidence interactions. 
•	Detect and log any tampering attempts or malicious activities. 
1.4 Scope 
CEIRS is a web-based platform targeting victims of cybercrime, digital forensic investigators, law enforcement agencies, and corporate cybersecurity departments. The system includes modules for incident management, evidence management, investigator assignment, governance, and administrative monitoring. The first version excludes mobile applications, AI-based threat classification, and external law enforcement integrations. 
 
2. Literature Review 
2.1 Blockchain in Digital Forensics 
Blockchain technology, characterised by immutability, transparency, and decentralisation, has been explored extensively for digital forensics applications. Several studies have proposed blockchain-based evidence management systems that ensure integrity and non-repudiation. The inherent properties of blockchain – cryptographic hashing, distributed ledger, and consensus mechanisms – make it an ideal foundation for preserving digital evidence. 
2.2 Chain of Custody 
Maintaining an unbroken chain of custody is fundamental to admissibility of digital evidence in court. Traditional methods rely on logs and signatures, which are susceptible to forgery. Blockchain-based custody logging ensures that every access, transfer, and modification is recorded immutably, providing a verifiable audit trail. 
2.3 IPFS and Decentralized Storage 
The InterPlanetary File System (IPFS) offers a content-addressed, peer-to-peer storage layer that complements blockchain. While blockchain stores small metadata and hashes, IPFS provides a scalable solution for storing large evidence files. Services like Pinata enable persistent pinning of IPFS content, ensuring availability. 
 
3. System Requirements 
3.1 Functional Requirements 
ID 	Feature 	Description 
FR-01 	User Registration 	Victims can register and log in securely. 
FR-02 	Incident Reporting 	Victims can submit cyber incident details (title, description, category, severity). 
FR-03 	Evidence Upload 	Victims can upload evidence files in multiple formats (images, PDFs, logs, etc.). 
FR-04 	Encryption & 
Hashing 	Files are encrypted (AES-GCM 256) and SHA-256 hashed before storage. 
ID 	Feature 	Description 
FR-05 	Blockchain 
Registration 	Evidence metadata and hashes are stored on a custom blockchain. 
FR-06 	Investigator 
Assignment 	System automatically assigns an officer based on workload and expertise. 
FR-07 	Chain of Custody 	Every evidence interaction (upload, verify, update, delete) is logged immutably. 
FR-08 	Investigation Updates 	Officers can record findings and update case status. 
FR-09 	Multi-Admin 
Governance 	Adding/removing officers requires unanimous admin approval. 
FR-10 	Violation Detection 	Tampering or deletion attempts generate violation blocks. 
FR-11 	Victim Transparency 	Victims can track investigation progress. 
 
3.2 Non-Functional Requirements 
NFR 	Requirement 
Security 	SHA-256 hashing, ECDSA signatures, AES-GCM 256 encryption, password hashing, role-based access. 
NFR 	Requirement 
Performance 	Evidence registration < 5 sec, verification < 2 sec, dashboard loading < 3 sec. 
Availability 	System uptime > 95%. 
Reliability 	Blockchain corruption detection and recovery. 
Scalability 	Supports up to 5 admins, 50 officers, 1,000 victims, 10,000 evidence records. 
Maintainability 	Modular architecture, clear separation of concerns, well-documented code. 
 
3.3 System Constraints 
•	No relational or NoSQL databases (blockchain is the source of truth). 
•	Evidence files are stored in an encrypted local vault  
•	All custody events are stored on the blockchain. 
 
4. System Architecture 
4.1 Architectural Overview 
CEIRS follows a layered architecture comprising: 
1.	Frontend Layer – HTML5, CSS3, Bootstrap 5, JavaScript. Provides responsive, accessible user interfaces for victims, officers, and admins. 
2.	Backend Layer – Flask (Python 3.12+) with RESTful APIs. Handles routing, authentication, session management, and business logic. 
3.	Blockchain Layer – A custom Python blockchain implementation with SHA-256 hashing, ECDSA signatures, proof-of-work (simulated), and JSON persistence. Stores all transactions (user, incident, evidence, custody, assignment, investigation, governance, violation). 

4.	Evidence Vault Layer – Local file system with AES-GCM 256 encryption. Stores encrypted evidence files, organised by case. Works alongside IPFS for decentralised off-chain storage. 
5.	Governance Layer – Multi-admin consensus for officer approvals, implemented via blockchain transactions. 4.2 Technology Stack 
Component 	Technology 
Frontend 	HTML5, CSS3, Bootstrap 5, JavaScript, Chart.js 
Backend 	Python 3.12+, Flask, Flask-Login, Flask-Session 
Blockchain 	Custom Python (SHA-256, ECDSA, JSON serialisation) 
Encryption 	Fernet (AES-GCM 256) for vault; PBKDF2 for key derivation 
IPFS 	Pinata API for file pinning 
Ethereum 	Web3.py, Sepolia testnet (optional) 
Deployment 	Local server (Windows/Linux) 
4.3 Blockchain Design 
Each block contains: 
•	index, timestamp, block_type, actor_id, public_key, transaction (dictionary), previous_ha sh, nonce, signature, current_hash. 
Block types: 
•	USER – user registration. 
•	INCIDENT – incident report. 
•	EVIDENCE – evidence metadata (hash, IPFS CID). 
•	CUSTODY – custody events. 
•	ASSIGNMENT – officer assignment. 
•	INVESTIGATION – investigation updates. 
•	GOVERNANCE – voting records. 
•	VIOLATION – security violations. 
 
4.4 Data Flow (Incident Reporting) 
  
4.5 Data Flow (Evidence Upload) 
  
4.6 Data Flow (Investigation) 
  
4.7 Data Flow (Tamper Detection) 
  
5. Implementation 
5.1 Module Structure 
 
The project is organised into the following Python packages: 
text 
CEIRS/ 
├── app.py 
├── config.py 
├── extensions.py 
├── seed_admins.py 
├── blockchain/ 
│   ├── __init__.py 
│   ├── block.py 
│   ├── blockchain.py 
│   ├── config.py 
│   ├── crypto_utils.py 
│   └── ethereum_client.py 
├── auth/ 
│   ├── routes.py 
│   ├── models.py 
│   └── utils.py 
├── key_management/ 
│   └── key_store.py 
├── evidence/ 
│   ├── routes.py 	BS-CYS-6TH N. 
│   ├── vault.py 
│   ├── encryptor.py 
│   ├── hasher.py 
│   ├── integrity.py 
│   └── pinata_service.py 
├── custody/ 
│   └── logger.py 
├── incident/ 
│   ├── routes.py 
│   └── service.py 
├── investigator/ 
│   ├── routes.py 
│   └── assignment.py 
├── victim/ 
│   └── routes.py 
├── admin/ 
│   └── routes.py 
├── violation/ 
│   └── detector.py 
├── governance/ 
│   └── routes.py 
└── templates/ 	BS-CYS-6TH N. 
    └── (all HTML templates) 
5.2 Key Implementation Details 
5.2.1 Blockchain Engine 
•	Block class stores all fields and provides compute_hash(), sign_block(), verify_signature(). 
•	Blockchain class manages chain persistence (chain.json), genesis block creation, block addition (with PoW), and chain validation. 
•	crypto_utils provides ECDSA key generation, signing, and verification using SECP256k1. 
5.2.2 Authentication & Roles 
•	User model (Flask-Login) loads user data from the latest USER block. 
•	Roles: USER, OFFICER, ADMIN. Officers require unanimous admin approval (PENDING_APPROVAL → ACTIVE). 
•	Login includes role dropdown to enforce role-based access. 
5.2.3 Evidence Management 
•	Upload: file → encrypted (system Fernet key) → stored in evidence_vault/ → SHA-256 hash → blockchain EVIDENCE block. 
•	Verification: retrieve file, decrypt, re-hash, compare with stored hash. 
•	Update: upload new file, create new EVIDENCE block with supersedes field. 
•	Delete: create EVIDENCE_REMOVED block (soft delete) and log violation. 
5.2.4 Chain of Custody 
•	log_custody_event() creates a CUSTODY block for every evidence interaction. 
•	Admin dashboard displays custody logs in the Audit & Security Log. 
5.2.5 Governance 
• 	Admin proposes officer → all admins vote (unanimous required) → new USER block with ACTIVE status. 
5.3 User Interfaces 
•	Landing page: Hero section with Login/Register buttons, stats cards, feature highlights. 
•	Victim Dashboard: Incident cards with upload form, evidence list. 
•	Officer Dashboard: Assigned cases, case view with evidence verification and update options. 
•	Admin Dashboard: Stats, pending approvals, officer management, cases, merged audit log (custody + violations). 
All pages feature a light/dark toggle and glass-morphism styling. 
 
6. Testing 
6.1 Unit Testing 
•	Blockchain hashing and signature verification. 
•	Evidence encryption/decryption. 
•	Authentication (password hashing, user retrieval). 
6.2 Integration Testing 
•	Flask ↔ Blockchain interactions. 
•	Evidence upload → vault → blockchain. 
•	Incident reporting → assignment → officer dashboard. 
6.3 Security Testing 
•	Tamper simulation: modify encrypted file → verification fails → violation block created. 
•	Unauthorised access: attempt to view case not assigned → access denied. 
•	Admin abuse: attempt to bypass governance → blockchain rejects. 
6.4 Performance Testing 
•	Evidence upload (10 MB file) completed within 5 seconds. 
•	Blockchain validation for 100+ blocks under 10 seconds. 
6.5 Test Results Summary 
All core functionalities passed. The system correctly detects and logs tampering, enforces role-based access, and maintains an immutable audit trail. 
 
7. Results and Discussion 
7.1 Functional Outcomes 
CEIRS successfully delivers: 
•	Secure incident reporting with role-based dashboards. 
•	Immutable evidence storage – SHA-256 hashes on the blockchain ensure integrity. 
•	Complete chain of custody – every action logged; deletion flagged as violation. 
•	Automated investigator assignment – workload and expertise balancing. 
•	Multi-admin governance – prevents unilateral abuse. 
•	Victim transparency – track investigation status. 
7.2 Security Analysis 
• 	Insider threat mitigation: Deleting evidence creates a violation block visible to all admins. 
•	Data integrity: Hash mismatch detection alerts admins. 
•	Non-repudiation: All actions digitally signed. 
•	No single point of failure: Blockchain is decentralised (single-node prototype, but extensible). 
7.3 Comparison with Existing Systems 
	Feature 	Traditional Systems 	CEIRS 
	Evidence Integrity 	Relies on trust 	Cryptographic verification 
	Chain of Custody 	Centralised logs 	Immutable blockchain records 
	Insider Threat 	Hard to detect 	Violation blocks automatically generated 
	Governance 	Single admin 	Multi-admin consensus 
	Transparency 	Limited 	Full audit trail 
	7.4 Limitations 
•	Single-node blockchain (not distributed). 
•	No real-time notifications (email/SMS). 
•	Prototype-level key management (private keys stored encrypted locally). 
•	Limited scalability for very large video files (future improvements). 
 
8.	Conclusion and Future Work 
8.1 Conclusion 
The CEIRS project successfully demonstrates the feasibility of using a custom Python blockchain to build a secure, transparent, and tamper-resistant cyber incident reporting and evidence management system. By combining blockchain immutability, encrypted storage, and multi-role governance, the system addresses the key challenges of insider threats, weak custody, and lack of transparency in traditional platforms. The prototype validates the core principles and provides a solid foundation for further development. 
8.2 Future Work 
•	Multi-node blockchain: Replace single-node with a distributed consensus network. 
•	AI forensics: Automate threat classification and anomaly detection. 
•	Mobile application: Extend accessibility for victims and officers. 
•	IPFS integration: Full decentralised storage (beyond Pinata). 
•	Email/SMS notifications: Real-time alerts for case updates and violations. 
•	Hardware security modules: Strengthen key management. 
