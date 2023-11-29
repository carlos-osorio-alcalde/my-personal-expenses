# My personal expense Tracker
This personal project is designed to track and manage personal expenses by leveraging various components. The system is composed of several interconnected pieces that work together seamlessly to provide a comprehensive expense tracking solution.

## Components
### 1. Expense Tracking API
The core of the system is an API built with FastAPI and Docker. This API is responsible for scraping transaction information from bank emails, extracting relevant details, and storing the data into an Azure SQL Server Database. The API features various endpoints to handle different events, and it incorporates OAuth2 for authentication to ensure secure access.

Deployment: The API is deployed on an EC2 instance.

### 2. Monitoring System
A monitoring system is implemented as an API, deployed in a serverless fashion using Azure Container Apps. This system generates a daily email summary of expenses, providing a convenient overview. The email is sent at 11:58 pm daily.

Deployment: Serverless deployment on Azure Container Apps.

### 3. Labeling API
To label transactions, a dedicated API is constructed using FastAPI and Docker. This API utilizes embeddings of merchant titles for labeling. For each new transaction, a comparison is made with 300 manually labeled transactions to determine the appropriate label.

Deployment: The Labeling API is deployed using Azure Container Apps.

### 4. Frontend
The frontend, built with Dash, serves as the user interface, assembling all components of the system. It provides a user-friendly interface to visualize and analyze summarized expense information.

Deployment: The frontend is deployed on an Azure Virtual Machine.

### 5. Transaction Update Cron Job
To ensure real-time tracking of transactions, a cron job runs inside a Virtual Machine every 10 minutes. This job checks for new transactions, extracts relevant details, labels them using the Labeling API, and updates the database. The necessary APIs are called with user credentials to facilitate this process.


## Usage

**Caution: This Project Involves Sensitive Information and Services**

Before proceeding with the usage of this project, it is crucial to exercise caution and adhere to the following considerations:

1. **Sensitive Information:**
   - Ensure that all sensitive information, including API keys, credentials, and tokens, is handled securely.
   - Review and update environment variables with the appropriate values for your setup.

2. **Email Token:**
   - Enable and configure the necessary token for accessing and scraping bank emails.
   - Exercise caution when dealing with email-related functionality, as it involves accessing personal and potentially sensitive information.

3. **Security Best Practices:**
   - Implement security best practices, such as using HTTPS, to safeguard communication between components.
   - Regularly review and update security configurations to address potential vulnerabilities.

4. **Contributions and Customization:**
   - If you plan to make contributions or customize the project for your needs, be mindful of the potential impact on security and data privacy.
   - Test thoroughly in a controlled environment before deploying any changes to a production setup.

5. **Documentation:**
   - Refer to the detailed documentation in each component's directory for specific deployment and configuration instructions.
   - Consult relevant cloud service documentation for additional security guidelines.
