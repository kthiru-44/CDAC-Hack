---
title: "Submitting Jobs"
category: "QSDK Sphinx Manual"
url: "https://qniverse.in/docs-category/qsdk/job_api/job_apis.html"
source_rst: "sources/job_api/job_apis.rst.txt"
---

# Submitting Jobs

> **Category:** QSDK Sphinx Manual | **Source:** [https://qniverse.in/docs-category/qsdk/job_api/job_apis.html](https://qniverse.in/docs-category/qsdk/job_api/job_apis.html)


# Submitting Jobs

The QSDK provides a set of functions for managing quantum execution workflows. These APIs enable users to submit circuits for execution, track job progress, retrieve execution results, inspect transpiled circuits, and manage previously submitted jobs.

All job operations require a valid authentication token.

**Function** : run()

**Description** : The `run()` function serves as the primary execution interface for quantum circuits. It validates execution parameters, checks for simulator compatibility with specific circuit features (like conditional gates), and dispatches the circuit to a configured backend for processing.

**Syntax:**
    
    
    ```python
    job = run(qc, backend, shots, token=token, job_name="testjob")
    ```

**Parameters:**

  * **qc** * (QniverseCircuit object)– The quantum circuit object containing the sequence of operations and registers to be executed.

  * **backend** * (Backend object) – An object defining the execution environment. This must include pre-configured processor, hpc, and simulator attributes.

  * **shots** * (int) – The number of times the circuit should be sampled.

  * **token** * (str) – API authentication token required for remote execution on specific backends.

  * **job_name** (str) – A custom label used to identify the execution task in the backend’s job history.

Note

  * Parameters marked with an asterisk **(*)** are mandatory.

  * job : An object that represents the quantum computation task submitted to the backend

Once submitted, the job is queued and executed according to the selected backend configuration.

# Retrieving Job Information

## Job Status

**Description** : Returns the execution status of the job, including whether it is currently running, completed successfully, or failed.

**Syntax:**
    
    
    ```python
    job.job_status()
    #or
    job_status(token, job_id)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

  * **job_id** * (int) : The unique ID of the job.

## Job Details

**Description** : Returns metadata associated with the specified job, such as Job name, Backend configuration, Submission timestamp etc.,

**Syntax:**
    
    
    ```python
    job.job_details()
    #or
    job_details(token, job_id)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

  * **job_id** * (int) : The unique ID of the job.

## Job Results

**Description** : Returns the final execution result of the job.

**Syntax:**
    
    
    ```python
    job.fetch_job_result()
    #or
    fetch_job_result(token, job_id)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

  * **job** * (int) : The unique ID of the job.

## Transpiled Code

**Description** : Returns the circuit code after transpilation. The output format (such as Cirq or Qiskit) depends on the simulator selected during backend configuration.

**Syntax:**
    
    
    ```python
    job.transpiled_code()
    #or
    transpiled_code(token,job_id)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

  * **job** * (int) : The unique ID of the job.

## List Backend

**Description** : Get available backend simulators.

**Syntax:**
    
    
    ```python
    job.get_backend()
    #or
    get_backend(token)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

## List Jobs

**Description** : List the quantum jobs user has run.

**Syntax:**
    
    
    ```python
    job.list_jobs()
    #or
    list_jobs(token)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

## Cancel Job

**Description** : Cancel the specified quantum job.

**Syntax:**
    
    
    ```python
    job.cancel_job()
    #or
    cancel_job(token, job_id)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

  * **job** * (int) : The unique ID of the job.

## Delete Job

**Description** : Delete the specified quantum job.

**Syntax:**
    
    
    ```python
    job.delete_job()
    #or
    delete_job(token, job_id)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

  * **job** * (int) : The unique ID of the job.

## Job Credit balance

**Description** : To retrieve the remaining credit balance.

**Syntax:**
    
    
    ```python
    job.credit_balance()
    #or
    credit_balance(token)
    ```

**Parameters:**

  * **token** * (str) : The user’s authentication token.

* * *
