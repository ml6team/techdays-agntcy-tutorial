# TechDays 2025 AGNTCY Workshop: Multi-Agent System Integration

## 🎯 Workshop Overview

Welcome to the **CoffeeAGNTCY Workshop**! In this TechDays tutorial, you'll learn to use the **AGNTCY framework** - a powerful multi-agent system development platform that enables you to build sophisticated agent ecosystems where multiple AI agents collaborate to solve complex problems.

**What You'll Build**: A multi-agent coffee trading system that answers questions about coffee supplies, manages inventory across multiple farms, and processes orders intelligently. The system demonstrates how agents work together using **MCP (Model Context Protocol) servers** to access external data sources like weather information.

Learn more about AGNTCY at [https://docs.agntcy.org/](https://docs.agntcy.org/).

## 📋 Learning Objectives

### Main Objectives
By the end of this workshop, you will:

- **Understand AGNTCY Framework**: Learn core concepts and architecture (Part 1)
- **Deploy Multi-Agent System**: Set up and configure the coffee trading system (Part 1)
- **Monitor Agent Interactions**: Use Grafana to visualize agent communications (Part 2)
- **Experience Group Conversations**: See multi-agent collaboration in logistics workflow (Part 3)

### Optional Objectives
If you have extra time:

- **Integrate Weather Awareness**: Add MCP client to Vietnam farm for monsoon detection (Part 4)

---

## 🏗️ System Architecture

The CoffeeAgntcy system models a **supervisor-worker agent ecosystem**:

### Core Components
- **Coffee Exchange (Supervisor)**: Manages inventory and fulfills orders
- **Coffee Farms (Workers)**: Supply inventory and process orders
  - Brazil Farm: Basic coffee production
  - Colombia Farm: Uses weather data for yield calculations
  - Vietnam Farm: **Possible Integration target** – needs monsoon awareness
- **Weather MCP Server**: Provides real-time weather data
- **SLIM Message Bus**: Enables agent communication
- **Observability Stack**: Grafana dashboard for monitoring

### Technology Stack
- **AGNTCY Framework**: Multi-agent orchestration
- **MCP (Model Context Protocol)**: External service integration
- **SLIM Transport**: Agent-to-agent communication
- **OpenTelemetry**: Distributed tracing
- **Grafana + ClickHouse**: Observability and monitoring

---
**Getting Started**: First, clone the CoffeeAgntcy repository from [https://github.com/agntcy/coffeeAgntcy](https://github.com/agntcy/coffeeAgntcy). Feel free to explore their README and experiment with the system. However, this tutorial contains all the setup instructions you need, so you can follow along step-by-step.

⚠️ **Important**: We'll be expanding the *lungo* configuration with new features. Make sure to work inside the `coffeeAGNTCY/coffee_agents/lungo` directory throughout this tutorial.

## 🚀 Part 1: Deploy the System

### Prerequisites

Ensure you have these tools installed:

- **uv** (Python package manager)
```sh
brew install uv
```

- **Node.js** (16.14.0+)
```sh
node -v
```

### Setup Instructions

1. **Environment Setup**
   
   Create a virtual environment:
   ```sh
   uv venv
   source .venv/bin/activate
   ```
   
   Copy the environment file:
   ```sh
   cp .env.example .env
   ```

2. **Configure LLM Provider**
   
   If you don't have an LLM API key available, our workshop team will provide you with one.

   You can choose between OpenAI and Azure OpenAI. Edit your `.env` file:

   **OpenAI:**
   ```env
   LLM_PROVIDER=openai
   OPENAI_API_KEY="your_openai_api_key_here"
   OPENAI_ENDPOINT=https://api.openai.com/v1
   OPENAI_MODEL_NAME=gpt-4o
   ```

   **Azure OpenAI:**
   ```env
   LLM_PROVIDER=azure-openai
   AZURE_OPENAI_ENDPOINT=https://your-azure-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=gpt-4-prod
   AZURE_OPENAI_API_KEY=your_azure_api_key
   AZURE_OPENAI_API_VERSION=2023-12-01-preview
   ```
3. **Configure Observability (OTEL)**
   ```env
   OTLP_HTTP_ENDPOINT=http://localhost:4318
   ```

4. **Configure SLIM Message Bus**
   ```env
   DEFAULT_MESSAGE_TRANSPORT=SLIM
   TRANSPORT_SERVER_ENDPOINT=http://localhost:46357
   ```

5. **Install Dependencies**
   ```sh
   uv sync
   ```

### Running the System

⚠️ **Important**: You'll need **7 terminal tabs** to run the complete system. For each new terminal, run these setup commands:

### Running the Services

You'll need to run different services in separate terminal tabs to get the entire system running.

1. **Start Services** (Each in a separate terminal tab)

> **Note:** Export the `PYTHONPATH` **on each new terminal** before running Python services. Also, don't forget to **activate your virtual environment**.
>
>```sh
>cd coffeeAGNTCY/coffee_agents/lungo
>source .venv/bin/activate
>export PYTHONPATH=$(pwd)
>```

- **Terminal 1 – SLIM Message Bus & Observability**
  ```sh
  docker-compose up slim nats clickhouse-server otel-collector grafana
  ```
  
  💡 **Tip:** If this command fails, make sure to delete any partially running containers by running `docker ps -a`.

- **Terminal 2 – Weather MCP Server**
  ```sh
  uv run python agents/mcp_servers/weather_service.py
  ```

- **Terminal 3 – Brazil Farm**
  ```sh
  uv run python agents/farms/brazil/farm_server.py
  ```

- **Terminal 4 – Colombia Farm**
  ```sh
  uv run python agents/farms/colombia/farm_server.py
  ```

- **Terminal 5 – Vietnam Farm**
  ```sh
  uv run python agents/farms/vietnam/farm_server.py
  ```

- **Terminal 6 – Coffee Exchange**
  ```sh
  uv run python agents/supervisors/auction/main.py
  ```

- **Terminal 7 – Frontend UI**
  ```sh
  cd frontend
  npm install
  npm run dev
  ```

If you need to update one of the services during the exercise, simply stop the process and rerun it! 

### Access the System

- **Coffee Exchange UI**: [http://localhost:5173](http://localhost:5173)
- **Grafana Dashboard**: [http://localhost:3001](http://localhost:3001) (default admin/admin)

---

## 🔍 Part 2: Explore the System

### Test Current Functionality

Try these prompts in the UI:

| Intent | Prompt | Expected Behavior |
|--------|--------|-------------------|
| **Check Inventory** | "How much coffee does the Colombia farm have?" | Shows current inventory with weather-adjusted yield |
| **View All Farms** | "Show me the total inventory across all farms" | Displays inventory from all three farms |
| **Vietnam Status** | "What's the current inventory at the Vietnam farm?" | Shows basic inventory (no weather integration yet) |

### Visualize OTEL Traces in Grafana

**What is Grafana?** Grafana is a monitoring and observability platform that helps you visualize data from your applications. In this workshop, we'll use it to see how agents communicate with each other and with external services.

1. **Open Grafana**: [http://localhost:3001](http://localhost:3001)
   Default credentials: `admin` / `admin`

2. **Connect to ClickHouse Database** (if not already connected):
   - Go to **Configuration** → **Data Sources** → **Add data source**
   - Search for "ClickHouse" and select it
   - Configure the connection:
     - **Server address:** `clickhouse-server`
     - **Port:** `9000`
     - **Protocol:** `native`
     - **User/Password:** `admin` / `admin`
   - Click **Save & Test**

3. **Import the OTEL Traces Dashboard**:
   - Go to **Dashboards** → **Import**
   - Upload the [`lungo_dashboard.json`](lungo_dashboard.json) file (this file contains pre-configured visualizations)
   - Select `grafana-clickhouse-datasource` as the data source
   - Click **Import**

4. **Explore Agent Interactions**:
   - The dashboard will show traces of agent communications
   - Look for traces from the Colombia farm when it queries the weather MCP server
   - You'll see the flow: Colombia Farm → Weather MCP Server → Response back to Farm
   - This helps you understand how your weather integration is working behind the scenes

---

## 🚚 Part 3: Group Conversation - Logistics System

### Overview

This section demonstrates a **logistics multi-agent conversation** where specialized agents collaborate to process coffee orders from start to finish. The system showcases how different agents handle specific aspects of the order lifecycle using the SLIM message bus for group communication.

### Logistics Architecture

The logistics system consists of four specialized agents:

| Agent | Role | Responsibilities |
|-------|------|------------------|
| **Logistic Supervisor** | Orchestrator | Starts workflow, handles user input, creates orders |
| **Tatooine Farm Agent** | Order Processor | Receives orders, prepares for shipping |
| **Shipper Agent** | Transportation | Handles customs clearance, final delivery |
| **Accountant Agent** | Payment Processor | Confirms payment completion |

### Order Lifecycle

```
User Order → [Supervisor] → RECEIVED_ORDER → [Farm]
[Farm] → HANDOVER_TO_SHIPPER → [Shipper] → CUSTOMS_CLEARANCE
[CUSTOMS_CLEARANCE] → [Accountant] → PAYMENT_COMPLETE → [Shipper] → DELIVERED
```



### Running the Logistics System


1. **Start Infrastructure** (if not already running):
   ```sh
   docker-compose up slim clickhouse-server otel-collector grafana
   ```

2. **Start Logistics Agents**:
   ```sh
   docker-compose up logistic-farm logistic-supervisor logistic-shipper logistic-accountant
   ```


### Testing the Logistics System

**Using the UI:**
Navigate to the Coffee Exchange UI and try prompts like:
- "I want to order 5000 lbs of coffee for $3.52 from the Tatooine farm"
- "Process an order for 1000 lbs of coffee"


### Logistics Observability

Monitor the logistics workflow in Grafana:
1. Open [http://localhost:3001](http://localhost:3001)
2. Import the **Group Conversation Dashboard** (`group_conversation_dashboard.json`)
3. Observe agent interactions and state transitions in real-time

---

## 🎯 Part 4: Challenge - Vietnam Farm Monsoon Integration

> **Note**: This is an optional challenge! The core learning objectives are achieved by understanding the system architecture and MCP server concepts from Parts 1-3.

### Problem Statement

The Vietnam farm currently doesn't query weather data. During monsoon season, yield reports are inaccurate, causing unfulfilled orders at the Coffee Exchange.

### Challenge Goals

1. **Enhance Weather MCP Server**
   - Implement monsoon detection in `agents/mcp_servers/weather_service.py`
   - Provide `monsoon_status` (True/False)
   - Include real-time weather metrics (wind speed, rainfall)

2. **Update Vietnam Farm Agent**
   - Modify `agents/farms/vietnam/agent.py` to query weather data
   - Reduce coffee yield by **30%** if monsoon detected
   - Include monsoon status in inventory reports

### Expected Behavior

- Monsoon status displayed: "There are monsoon conditions." or "There are no monsoon conditions."
- Yield adjusted by 30% during monsoon season
- Real weather data from MCP server (not hardcoded)
- Grafana traces showing MCP calls

### Implementation Guide

#### Step 1: Weather MCP Server Enhancement

**File:** `agents/mcp_servers/weather_service.py`

- **Implement the following function:**

```python
async def get_monsoon_status(location: str):
    # 1. Retrieve weather forecast (see get_forecast for example)
    # 2. If wind speed > 8 m/s, consider it monsoon season
    # 3. Return a descriptive message with wind speed
    # 4. Handle errors gracefully
```

#### Step 2: Vietnam Farm Agent Integration

**File:** `agents/farms/vietnam/agent.py`

- **Implement the monsoon check node:**

```python
async def _monsoon_check_node(self, state: GraphState) -> dict:
    # 1. Initialize AGNTCY factory
    # 2. Create transport for MCP communication
    # 3. Create MCP client connected to the weather server
    # 4. Call get_monsoon_status asynchronously
    # 5. Extract concise status line:
    #    "There are monsoon conditions." or "There are no monsoon conditions."
    # 6. Return updated state with monsoon_status
```

- **Update the agent workflow:**
  - Ensure the supervisor node routes inventory queries through the monsoon check node
  - In `_build_graph`, add the new node and edges as needed

- **Update the inventory node:**
  - Modify `_inventory_node` to use `monsoon_status` from the state
  - Adjust yield estimates: **reduce by 30% if monsoon detected**
  - Include the monsoon status line in the AI prompt

#### Step 3: UI Configuration Update

Update the frontend graph configuration:
```sh
cp graphConfigs_workshop.tsx frontend/src/utils/graphConfigs.tsx
```

#### Step 4: Testing

**Testing Checklist**

- Try basic queries:
  - "How much coffee do we have in stock in Vietnam?"
  - "What's the status of order 12345?"
- Try monsoon-related queries:
  - "What's the current inventory at the Vietnam farm?"
  - "Show me Vietnam farm's coffee inventory"

**What to Look For:**

- ✅ The response includes a monsoon status line.
- ✅ Coffee yield is reduced by 30% if monsoon conditions are detected.
- ✅ Inventory amounts reflect current weather conditions.
- ✅ MCP (weather) calls from the Vietnam farm appear in Grafana traces.
- ❌ If you don't see a monsoon status, or inventory doesn't change with weather, or there are errors in the Vietnam farm terminal, or no MCP traces in Grafana, something is wrong.

**Summary of Success Criteria**

- Vietnam farm accurately reports monsoon status and weather-adjusted yield.
- MCP server provides weather data to the farm agent.
- Grafana shows traces of MCP interactions.
- All other system functionality continues to work as before.

---

## ✨ Bonus: Add More MCP Servers

Congratulations on making it this far, this is no small feat! The Vietnam farm monsoon integration is a challenging task we've proposed - it's not trivial, so don't worry if you don't have much time left to complete it. The core learning objectives are achieved by understanding the system architecture and MCP server concepts.

If you have additional time and want to further expand the system, try implementing extra MCP servers to enrich the coffee trading platform:

**Suggested MCP Server Ideas:**
- **Market Price Server**: Get real-time coffee commodity prices from financial APIs
- **Shipping Logistics Server**: Check shipping routes, costs, and delivery times
- **Quality Control Server**: Analyze coffee bean quality metrics and certifications
- **Sustainability Server**: Track carbon footprint and sustainability scores
- **News Server**: Monitor coffee industry news and market trends
- **Inventory Optimization Server**: Suggest optimal inventory levels based on demand patterns

**Implementation Tips:**
- Follow the same pattern as the weather server
- Use async/await for external API calls
- Add proper error handling
- Update the graph configuration to include new connections
- Test with creative prompts that utilize your new servers

---

## 📚 Resources

There is a lot more that AGNTCY can do. Don't hesitate to explore the [original AGNTCY repo](https://github.com/agntcy/coffeeAgntcy) and their [documentation](https://docs.agntcy.org/).

---

# **Happy coding!** 🚀☕

Focus not just on making it work, but understanding how multi-agent systems integrate external services and communicate effectively.

