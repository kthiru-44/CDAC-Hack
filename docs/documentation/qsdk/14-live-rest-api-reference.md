---
title: "QACC Live REST API Reference & Execution Endpoints"
category: "QSDK"
url: "https://qniverse.in/wp-json/qacc/v1/"
---

# QACC Live REST API Reference & Execution Endpoints

> **Category:** QSDK & Cloud Infrastructure | **Base URL:** `https://qniverse.in/wp-json/qacc/v1`

The Qniverse platform exposes a REST API under the namespace `/qacc/v1` that powers the QSDK Python package and remote job submission to **C-DAC PARAM Supercomputers** (`Param_Utkarsh`) and the **QACC Cluster** (`QACC_Cluster`).

---

## 1. Authentication

All requests to `/qacc/v1/*` require an HTTP `Authorization` header containing a JSON Web Token (JWT) issued by Qniverse:

```http
Authorization: Bearer <YOUR_QNIVERSE_JWT_TOKEN>
```

Tokens are configured in your `.env` file:
```bash
QNIVERSE_API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

## 2. Cluster & Backend Endpoints

### 2.1 Get Available Backends
Retrieve all available High-Performance Computing (HPC) clusters, processor types (CPU / GPU), and supported quantum simulators.

- **Method:** `GET`
- **Endpoint:** `/wp-json/qacc/v1/backends`
- **Headers:** `Authorization: Bearer <TOKEN>`

#### Example Response:
```json
{
  "data": [
    {
      "hpc": "Param_Utkarsh",
      "processor": {
        "CPU": {
          "simulator": [
            "aer_simulator_density_matrix",
            "aer_simulator_statevector",
            "cirq_simulator",
            "qasm_simulator"
          ]
        },
        "GPU": {
          "simulator": [
            "aer_simulator_statevector_gpu"
          ]
        }
      }
    },
    {
      "hpc": "QACC_Cluster",
      "processor": {
        "CPU": {
          "simulator": [
            "aer_simulator_density_matrix",
            "aer_simulator_statevector",
            "cirq_simulator",
            "qasm_simulator",
            "qsimcirq_simulator",
            "quest_simulator",
            "qulacs_multicpu_simulator"
          ]
        },
        "GPU": {
          "simulator": [
            "aer_simulator_statevector_gpu",
            "nvidia_cudaq_statevector_simulator",
            "qsimcirq_cuquantum_gpu_simulator"
          ]
        }
      }
    }
  ]
}
```

---

### 2.2 Query Processor Information
Query simulator availability by processor architecture (`CPU` or `GPU`).

- **Method:** `GET`
- **Endpoint:** `/wp-json/qacc/v1/processor-info?processor={CPU|GPU}`
- **Headers:** `Authorization: Bearer <TOKEN>`

#### Example Request:
```bash
curl -sL -H "Authorization: Bearer $QNIVERSE_API_KEY" \
  "https://qniverse.in/wp-json/qacc/v1/processor-info?processor=GPU"
```

#### Example Response:
```json
{
  "status": "success",
  "data": [
    {
      "hpc_cluster": "Param_Utkarsh",
      "simulators": [
        "aer_simulator_statevector_gpu"
      ]
    },
    {
      "hpc_cluster": "QACC_Cluster",
      "simulators": [
        "aer_simulator_statevector_gpu",
        "nvidia_cudaq_statevector_simulator",
        "qsimcirq_cuquantum_gpu_simulator"
      ]
    }
  ]
}
```

---

## 3. Remote Job Submission & Lifecycle Endpoints

### 3.1 Submit a Job
Submits a quantum circuit or transpiled payload to a target backend for execution.

- **Method:** `POST`
- **Endpoint:** `/wp-json/qacc/v1/submit-job`
- **Headers:**
  - `Authorization: Bearer <TOKEN>`
  - `Content-Type: application/json`

#### Payload Schema:
```json
{
  "hpc": "Param_Utkarsh",
  "processor": "CPU",
  "simulator": "aer_simulator_statevector",
  "shots": 1024,
  "circuit_code": "...",
  "format": "qasm3"
}
```

---

### 3.2 List User Jobs
Lists all previous and current execution jobs submitted by the authenticated user.

- **Method:** `GET`
- **Endpoint:** `/wp-json/qacc/v1/jobs`
- **Headers:** `Authorization: Bearer <TOKEN>`

#### Example Response:
```json
{
  "jobs": []
}
```

---

### 3.3 Query Job Status
Checks the live status of a job.

- **Method:** `GET`
- **Endpoint:** `/wp-json/qacc/v1/jobs/{job_id}/status`
- **Headers:** `Authorization: Bearer <TOKEN>`

#### Status Values:
- `QUEUED`: Waiting in HPC scheduler queue.
- `RUNNING`: Actively simulating on cluster node.
- `COMPLETED`: Simulation finished; results available.
- `FAILED`: Execution encountered an error.

---

### 3.4 Retrieve Job Results
Retrieves measurement counts, probability distributions, or statevector amplitudes.

- **Method:** `GET`
- **Endpoint:** `/wp-json/qacc/v1/jobs/{job_id}/results`
- **Headers:** `Authorization: Bearer <TOKEN>`

---

### 3.5 Cancel a Job
Cancels a queued or executing job on the HPC cluster.

- **Method:** `POST`
- **Endpoint:** `/wp-json/qacc/v1/jobs/{job_id}/cancel`
- **Headers:** `Authorization: Bearer <TOKEN>`
