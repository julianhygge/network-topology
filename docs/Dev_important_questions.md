# Five Most Important Questions for P2P Simulator Developers

## 1. What is the overall architecture and purpose of the P2P Simulator?
   
The P2P Simulator is designed to model and analyze the behavior of local energy communities (microgrids). It simulates energy generation, consumption, and sharing within these communities over time to understand energy flows, optimize distribution, assess configurations, and evaluate potential benefits. The system follows a 3-layer architecture:
   
- **API Layer**: Handles HTTP requests, routing, and data validation using FastAPI
- **Domain Layer**: Contains core business logic and services
- **Data Layer**: Manages data persistence using PostgreSQL with Peewee ORM

## 2. How is the network topology modeled in the system?
   
The network topology follows a hierarchical structure:
   
- Localities contain Substations
- Substations contain Transformers
- Transformers connect to Houses
- Houses can have load profiles, solar generation, and batteries
   
This is implemented through a Node model that creates a tree structure, with each node having a specific type (substation, transformer, or house) and potentially having children nodes. This allows for modeling complex electrical grid topologies.

## 3. How are load profiles and energy generation/consumption modeled?
   
The system models:
   
- Load profiles for houses (consumption patterns)
- Solar generation capabilities (with parameters like capacity in kW)
- Battery storage (with parameters for charging/discharging rates and capacity)
   
These components allow for simulating realistic energy usage and generation patterns within the microgrid. The load profiles appear to be configurable, and there are predefined templates available.

## 4. What authentication and authorization mechanisms are implemented?
   
The system uses:
   
- OTP (One-Time Password) based authentication via phone numbers
- JWT tokens for maintaining sessions
- Role-based access control with permissions tied to specific resources
- Groups that can be assigned to users, with each group having specific roles
   
This provides a flexible security model where users can be assigned to groups, groups have roles, and roles have specific permissions on resources.

## 5. How can a developer extend the system with new functionality?
   
To extend the system, a developer would typically:
   
- Add new models in the data layer (schemas)
- Implement repositories for data access
- Create service classes in the domain layer for business logic
- Define API endpoints in the resources directory
- Update dependency injection container to provide the new services
   
The system follows clean architecture principles with dependency injection, making it modular and extensible. New features should follow the established patterns of repositories, services, and API resources.
