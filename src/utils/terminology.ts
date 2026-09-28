export interface TermDefinition {
  short: string
  title: string
  plainTitle: string
  explanation: string
  technicalDetails?: string
  inputs?: string[]
}

export const terminology: Record<string, TermDefinition> = {
  EAL: {
    short: 'EAL',
    title: 'Expected Annual Loss',
    plainTitle: 'Expected Yearly Loss',
    explanation: 'Estimated financial loss the organization could incur from cyber incidents over one year based on current risk exposure.',
    technicalDetails: 'Statistical expectation calculated by multiplying event likelihoods by financial impact estimates across all attack vectors.',
    inputs: ['Asset Valuations', 'Threat Likelihood', 'Vulnerability Severities', 'Existing Control Efficacy'],
  },
  VaR95: {
    short: 'VaR95',
    title: '95% Value at Risk',
    plainTitle: 'Worst-Case Loss Estimate',
    explanation: 'Estimated loss level that should not be exceeded in 95% of simulated high-severity cyber incident scenarios.',
    technicalDetails: '95th percentile of the Monte Carlo financial loss distribution curve, representing tail risk exposure.',
    inputs: ['Monte Carlo Simulations (10,000 runs)', 'Loss Distributions', 'Cascading Impact Vectors'],
  },
  ROSI: {
    short: 'ROSI',
    title: 'Return on Security Investment',
    plainTitle: 'Return from Security Protection',
    explanation: 'Shows how many rupees of cyber risk reduction are achieved for every ₹1 spent on a security control.',
    technicalDetails: 'Formula: (Risk Reduction - Annual Cost of Control) / Annual Cost of Control, expressed as a ROI ratio multiplier.',
    inputs: ['Baseline EAL', 'Post-Control EAL', 'Annualized Control Implementation & Maintenance Cost'],
  },
  digitalTwin: {
    short: 'Digital Twin',
    title: 'Enterprise Attack-Path Graph',
    plainTitle: 'Live Model of Your IT Environment',
    explanation: 'An interactive 3D model mapping servers, cloud accounts, employee identities, weaknesses, and security controls.',
    technicalDetails: 'Graph model mapping directed relationships (A -> B) representing reachable attack paths toward Crown Jewels.',
    inputs: ['Asset Discovery Telemetry', 'IAM Identity Permissions', 'Vulnerability Scans', 'Network Segmentation Rules'],
  },
  attackPath: {
    short: 'Attack Path',
    title: 'Exploit Execution Chain',
    plainTitle: 'Possible Route an Attacker Could Take',
    explanation: 'Shows how an attacker could move step-by-step from an exposed entry point to reach your most critical systems.',
    technicalDetails: 'Sequence of connected nodes where breach probability > 0, leading to a Crown Jewel asset node.',
    inputs: ['CVE Vulnerability Records', 'Privilege Escalation Routes', 'Network Access Control Lists'],
  },
  monteCarlo: {
    short: 'Monte Carlo',
    title: 'Stochastic Risk Simulation',
    plainTitle: 'Risk Simulation Engine',
    explanation: 'Runs thousands of simulated cyberattack scenarios to produce an accurate financial risk distribution.',
    technicalDetails: '10,000 iteration probabilistic sampling model incorporating Beta-PERT likelihood distributions.',
    inputs: ['Historical Breach Data', 'Threat Actor Capabilities', 'Asset Financial Impact Profiles'],
  },
  counterfactual: {
    short: 'Counterfactual',
    title: 'Security Control What-If Simulation',
    plainTitle: 'Protection Scenario Analysis',
    explanation: 'Simulates the exact financial impact and risk reduction of implementing a new security safeguard before spending money.',
    technicalDetails: 'Submodular function optimization measuring delta EAL upon introducing or modifying specific control nodes.',
    inputs: ['Proposed Control Parameters', 'Path Vulnerability Mitigation Factors'],
  },
  riskContributors: {
    short: 'Risk Contributors',
    title: 'Material Exposure Drivers',
    plainTitle: 'What Is Driving Your Cyber Risk?',
    explanation: 'The specific systems, accounts, and weaknesses that account for the largest share of your total financial exposure.',
    technicalDetails: 'Attributable EAL per asset node derived from graph centralities and vulnerability weights.',
  },
  compliance: {
    short: 'Compliance Matrix',
    title: 'Regulatory Cross-Reference Ledger',
    plainTitle: 'Regulatory Security Audit Trail',
    explanation: 'Maps security protections directly to mandatory regulations like ISO 27001, NIST CSF, RBI CSF, and SEBI CSCRF.',
    technicalDetails: 'Traceable mapping connecting control evidence objects to specific compliance framework clauses.',
  },
  telemetry: {
    short: 'Telemetry Stream',
    title: 'Real-Time Event Audit Log',
    plainTitle: 'Live Security Activity Stream',
    explanation: 'Shows live updates as security events occur, protections are enabled, or new vulnerabilities are detected.',
    technicalDetails: 'Event stream processor recording state changes and updating the Digital Twin graph state dynamically.',
  },
}
