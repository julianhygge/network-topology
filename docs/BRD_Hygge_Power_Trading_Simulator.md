# Business Requirements Document (BRD) - Hygge Power Trading Simulator

**Version:** 0.1  
**Date:** 20/July/2024

---

## 1. Introduction

The goal of this project is to simulate a peer-to-peer (P2P) energy trading platform called "Hygge Power Trading Simulator" where consumers and prosumers can trade energy using different bid types and dynamic pricing mechanisms.

---

## 2. Purpose

To build an educational and testing platform for understanding how P2P energy markets work in a simulated environment.

---

## 3. Scope

- Simulate a power grid with households (prosumers and consumers)
- Allow users to configure energy profiles and simulate market bidding
- Simulate 3 types of bids:
  - **Day ahead**
  - **Monthly**
  - **Preferential Exchange of Energy**
- View and analyze the simulation results

---

## 4. Stakeholders

- Students and researchers
- Software developers
- Utility companies
- Regulatory bodies

---

## 5. Functional Requirements

- Register/login as consumer or prosumer
- Upload/import grid topology
- Assign profiles to nodes (houses)
- Define bid parameters and constraints
- Launch simulations and view results
- Export simulation data

---

## 6. Non-Functional Requirements

- Web-based platform
- Fast execution of simulations
- Clean, intuitive UI
- Modular, extensible architecture
- Support for importing/exporting configuration and results

---

## 7. Assumptions and Dependencies

- Users understand basic concepts of energy trading and simulation
- All simulations are virtual and not connected to a real grid

---

## 8. Acceptance Criteria

- User can successfully run a simulation after configuring topology and profiles
- Simulation results are accurate and exportable
- UI provides meaningful feedback during setup and execution

---

## 9. Glossary

- **Prosumer:** A user who both produces and consumes energy
- **Consumer:** A user who only consumes energy
- **Topology:** Layout of the electrical network
- **Profile:** A time series representing energy usage or generation
- **Bid:** Offer to buy or sell energy at a certain price/time

