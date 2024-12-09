# Full Guide to Running the Application
This is a backend for display Agent Tool Calling through Websocket. For frontend, refer to the link: 

## Overview
This guide provides detailed instructions on how to set up and run the gateway and aiengine components of the application using Python. The application utilizes FastAPI for web services and RabbitMQ for message handling.

## Prerequisites
- Python 3.9 or higher installed on your machine.
- RabbitMQ server running locally.

## Directory Structure

## Setup Instructions
1. **Install Dependencies**  
   Navigate to both the gateway and aiengine directories and install the required packages using pip.  
   For the gateway:  
   ```bash
    cd gateway
    pip install -r requirements.txt
   ```  
   For the aiengine:  
   ```bash
    cd aiengine
    pip install -r requirements.txt
   ```

2. **Run the RabbitMQ Server**  
   If you don't have RabbitMQ installed, you can run it using Docker. Open a terminal and execute the following command:  
   ```bash
   docker run -d --hostname my-rabbit --name some-rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
   ```  
   This command will run RabbitMQ with the management plugin enabled, allowing you to access the management interface at [http://localhost:15672](http://localhost:15672) (default username and password are both guest).

3. **Run the Gateway**  
   Open a terminal and navigate to the gateway directory, then run the FastAPI application:  
   ```bash
    cd gateway
    python main.py
   ```

4. **Run the AI Engine**  
   Open another terminal and navigate to the aiengine directory, then run the FastAPI application:  
   ```bash
    cd aiengine
    python main.py
   ```

## Accessing the Services
- The gateway service will be accessible at [http://localhost:8000](http://localhost:8000).
- The aiengine service will be accessible at [http://localhost:8081](http://localhost:8081).

## Code Overview
### Gateway Component
- `main.py`: Handles WebSocket connections and manages communication between clients and the RabbitMQ message broker.
  - WebSocket endpoint: `@app.websocket("/ws/{conversation_id}")`
  - Connection management: `ConnectionManager` class.

### AI Engine Component
- `main.py`: Manages the AI agent's responses and interactions.
  - Streaming endpoint: `@app.post("/streaming")`
  - Uses the agent to process input and generate responses.

### RabbitMQ Client
- `rabbitmq_client.py`: Manages interactions with the RabbitMQ message broker.
  - Methods for connecting, sending, and consuming messages.

### Publisher
- `publisher.py`: Publishes messages to the RabbitMQ queue.

### Agent
- `agent.py`: Contains the logic for running the AI agent.
- `PhiAgent.py`: Defines the `PhiAgent` class and its methods for processing input and generating responses.

## Conclusion
This guide provides a comprehensive overview of setting up and running the application. Ensure that all dependencies are installed and that the RabbitMQ server is running before starting the services. If you encounter any issues, check the logs for errors and ensure that the configurations are correct.