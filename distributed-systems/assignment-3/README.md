<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Resilient Distributed Systems</h3>

  <p align="center">
    A hands-on implementation of resilience patterns and chaos engineering in microservices deployed on Kubernetes
    <br />
    <a href="https://github.com/vijethph/college-assignments"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/vijethph/college-assignments">View Demo</a>
    ·
    <a href="https://github.com/vijethph/college-assignments/issues/new?labels=bug&template=bug-report---.md">Report Bug</a>
    ·
    <a href="https://github.com/vijethph/college-assignments/issues/new?labels=enhancement&template=feature-request---.md">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#architecture">Architecture</a></li>
    <li><a href="#testing">Testing</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

This project demonstrates production-grade resilience patterns in distributed systems through practical implementation and chaos engineering experiments. It showcases how modern microservices architectures handle failures gracefully, maintain availability, and achieve self-healing capabilities.

**Why This Project Matters:**

- **Failures are inevitable** in distributed systems - this project shows how to design for them, not around them
- **Real-world validation** through chaos engineering experiments proving that resilience patterns actually work
- **Quantified improvements**: faster failure response, increase in success rates, automatic recovery in 37 seconds
- **Production-ready patterns** used at scale

The project implements a client-server microservices architecture on Kubernetes, featuring:

- Circuit Breaker pattern for preventing cascading failures
- Retry with Exponential Backoff and Jitter for handling transient failures
- Chaos engineering experiments validating system resilience under realistic failure conditions
- Comprehensive observability with structured logging and metrics

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![Python][Python.org]][Python-url]
- [![FastAPI][FastAPI.tiangolo.com]][FastAPI-url]
- [![Kubernetes][Kubernetes.io]][Kubernetes-url]
- [![Docker][Docker.com]][Docker-url]

**Core Technologies:**

- **Python 3.11** - Modern Python with type hints and async support
- **FastAPI** - High-performance async web framework for microservices
- **httpx** - Modern HTTP client with timeout and connection pooling
- **tenacity** - Robust retry library with exponential backoff and jitter
- **structlog** - Structured logging for observability
- **Kubernetes** - Container orchestration platform
- **Minikube** - Local Kubernetes cluster for development
- **Chaos Toolkit** - Open-source chaos engineering platform

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Key Features

- **Circuit Breaker Pattern** - Fast-fail protection with automatic recovery
- **Retry with Exponential Backoff** - Intelligent handling of transient failures
- **Chaos Engineering** - Automated failure injection and validation
- **Comprehensive Testing** - Baseline, resilience, and chaos experiment suites
- **Full Observability** - Structured logging and circuit breaker metrics
- **Production-Ready** - Battle-tested patterns with quantified trade-offs
- **Self-Healing** - Automatic recovery without manual intervention
- **Kubernetes Native** - Service discovery, health checks, and rolling deployments

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.11 or higher**

  ```sh
  python --version
  ```

- **pipenv** - Python dependency management

  ```sh
  pip install pipenv
  ```

- **Docker** - Container runtime

  ```sh
  docker --version
  ```

- **Minikube v1.32.0 or higher** - Local Kubernetes cluster

  ```sh
  minikube version
  ```

- **kubectl** - Kubernetes CLI

  ```sh
  kubectl version --client
  ```

- **jq** - JSON processor (for chaos experiments)
  ```sh
  sudo apt-get install jq  # Ubuntu/Debian
  brew install jq          # macOS
  ```

### Installation

1. **Clone the repository**

   ```sh
   git clone https://github.com/vijethph/college-assignments.git
   cd k8s-assignment
   ```

2. **Install Python dependencies**

   ```sh
   pipenv install
   ```

3. **Start Minikube**

   ```sh
   minikube start
   ```

   Verify Minikube is running:

   ```sh
   kubectl get nodes
   ```

4. **Build Docker images**

   ```sh
   chmod +x scripts/build.sh
   ./scripts/build.sh
   ```

   This builds both `backend-service` and `client-service` images.

5. **Deploy to Kubernetes**

   ```sh
   chmod +x scripts/deploy.sh
   ./scripts/deploy.sh
   ```

   Wait for pods to be ready:

   ```sh
   kubectl get pods -w
   ```

6. **Verify deployment**

   ```sh
   # Check all pods are running
   kubectl get pods

   # Test client service
   minikube service client-service --url
   curl http://$(minikube ip):30090/health
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

### Quick Start

Test the system with default configuration:

```sh
chmod +x scripts/test.sh
./scripts/test.sh
```

This runs basic health checks and demonstrates the resilience patterns in action.

### Manual Testing

**1. Access the services:**

```sh
# Get service URLs
minikube service client-service --url
minikube service backend-service --url

# Test endpoints
curl http://$(minikube ip):30090/health           # Client health check
curl http://$(minikube ip):30090/fetch-data       # Fetch data through client
curl http://$(minikube ip):30090/circuit-status   # View circuit breaker state
```

**2. Configure failure injection:**

```sh
# Set 50% failure rate with HTTP 500 errors
curl -X POST http://$(minikube ip):30080/config/failure \
  -H "Content-Type: application/json" \
  -d '{"failure_rate": 0.5, "status_code": 500}'

# Set 2-second delay on 50% of requests
curl -X POST http://$(minikube ip):30080/config/latency \
  -H "Content-Type: application/json" \
  -d '{"delay_ms": 2000, "delay_rate": 0.5}'

# View current configuration
curl http://$(minikube ip):30080/config
```

**3. Observe resilience patterns:**

```sh
# Watch client logs for circuit breaker and retry events
kubectl logs -l app=client-service -f
```

### Continuous Load Testing

Generate continuous traffic for observing system behavior over time:

```sh
# Forward port in background
kubectl port-forward svc/client-service 9090:9090 &

# Run load generator (1 request per second)
chmod +x scripts/load_generator.sh
./scripts/load_generator.sh http://localhost:9090 1
```

Press `Ctrl+C` to stop the load generator.

_For more examples and detailed testing procedures, please refer to the [Testing](#testing) section._

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ARCHITECTURE -->

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │  ┌─────────────────┐         ┌─────────────────┐     │ │
│  │  │ Client Service  │         │ Backend Service │     │ │
│  │  │                 │         │                 │     │ │
│  │  │  - Port: 9090   │────────▶│  - Port: 8000   │     │ │
│  │  │  - NodePort:    │  HTTP   │  - ClusterIP +  │     │ │
│  │  │    30090        │ Request │    NodePort:    │     │ │
│  │  │                 │         │    30080        │     │ │
│  │  │  ┌───────────┐  │         │                 │     │ │
│  │  │  │ Circuit   │  │         │  Configurable:  │     │ │
│  │  │  │ Breaker   │  │         │  - Failures     │     │ │
│  │  │  └───────────┘  │         │  - Latency      │     │ │
│  │  │  ┌───────────┐  │         │                 │     │ │
│  │  │  │ Retry +   │  │         └─────────────────┘     │ │
│  │  │  │ Backoff   │  │                                  │ │
│  │  │  └───────────┘  │                                  │ │
│  │  └─────────────────┘                                  │ │
│  │                                                         │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

**Backend Service:**

- FastAPI service providing data endpoints
- Configurable failure injection (rate, status codes)
- Configurable latency injection (delay duration, rate)
- Single replica for consistent test configuration
- Exposed via ClusterIP (internal) and NodePort (testing)

**Client Service:**

- FastAPI service that consumes backend service
- Implements Circuit Breaker pattern (threshold: 5, timeout: 30s)
- Implements Retry with Exponential Backoff (max 3 attempts)
- Single replica
- Exposed via NodePort for external access

**Kubernetes Resources:**

- **Deployments**: Manage pod lifecycle and scaling
- **Services**: Provide stable networking and service discovery
  - `backend-service`: ClusterIP + NodePort (8000:30080)
  - `client-service`: NodePort (9090:30090)
- **DNS**: Client uses `http://backend-service:8000` for internal communication

### Resilience Patterns

**1. Circuit Breaker**

```
CLOSED (Normal) ──[5 failures]──▶ OPEN (Fast-fail)
      ▲                               │
      │                               │ [30s timeout]
      │                               ▼
      └───[test success]─── HALF-OPEN (Testing)
                                      │
                          [test fails]┘
```

- **Purpose**: Prevent cascading failures, protect client from overload
- **Configuration**: 5 failure threshold, 30s timeout, 1 test call in HALF-OPEN
- **Benefit**: 4000x faster response (<10ms vs 30s timeout)

**2. Retry with Exponential Backoff**

```
Attempt 1 ──[fail]──▶ Wait ~1s ──▶ Attempt 2 ──[fail]──▶ Wait ~2s ──▶ Attempt 3
   │                                    │                                   │
   └─[success]                         └─[success]                        └─[success/fail]
```

- **Purpose**: Handle transient failures automatically
- **Configuration**: Max 3 attempts, exponential backoff (1s base, 2x multiplier), jitter
- **Benefit**: 75% improvement in success rate (50% → 87.5%)

**Pattern Integration:**

- Transient errors (503, 429) → Retry pattern
- Systemic errors (500, connection refused) → Circuit breaker
- Combined: 96.6% success rate despite 30% backend failures

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- TESTING -->

## Testing

### Test Suite Overview

The project includes comprehensive test scripts demonstrating baseline behavior, resilience patterns, and chaos engineering experiments.

| Test Type             | Script                        | Duration | Purpose                                          |
| --------------------- | ----------------------------- | -------- | ------------------------------------------------ |
| **Baseline**          | `baseline_test.sh`            | ~2 min   | Demonstrate behavior WITHOUT resilience patterns |
| **Circuit Breaker**   | `test_circuit_breaker.sh`     | ~2 min   | Validate circuit breaker states and transitions  |
| **Retry Pattern**     | `test_retry.sh`               | ~2 min   | Validate retry with exponential backoff          |
| **Combined**          | `test_resilience_patterns.sh` | ~3 min   | Both patterns working together                   |
| **Chaos Engineering** | `chaos_experiment.sh`         | ~2 min   | Pod deletion and auto-recovery                   |

### Part A: Baseline Tests

Demonstrates system behavior **without** resilience patterns:

```sh
chmod +x scripts/baseline_test.sh
./scripts/baseline_test.sh
```

**What it tests:**

- Direct error propagation (no recovery)
- No retry logic (single failures cause request failures)
- Blocking on delays (thread exhaustion risk)
- No fallback mechanism (complete dependency on backend)

**Key observations:**

- 50% backend failure → 50% client failure (no improvement)
- 3-second delays → 3-second blocking (no fast-fail)
- 100% backend failure → all requests fail independently

### Part B: Resilience Pattern Tests

#### Test 1: Circuit Breaker

```sh
chmod +x scripts/test_circuit_breaker.sh
./scripts/test_circuit_breaker.sh
```

**Demonstrates:**

1. **CLOSED → OPEN**: Opens after 5 consecutive failures
2. **Fast-fail**: <10ms response time while OPEN
3. **OPEN → HALF-OPEN**: Attempts test call after 30s timeout
4. **Re-opening**: Circuit re-opens if test fails
5. **HALF-OPEN → CLOSED**: Closes when backend recovers

**Expected output:**

```
Phase 1: Normal operation (CLOSED, 0 failures)
Phase 2: Triggering failures (5 failures → OPEN)
Phase 3: Fast-fail mode (<10ms responses)
Phase 4: Waiting for timeout (30 seconds)
Phase 5: Test call with failed backend (HALF-OPEN → OPEN)
Phase 6: Test call with healthy backend (HALF-OPEN → CLOSED)
Circuit breaker working correctly
```

#### Test 2: Retry with Exponential Backoff

```sh
chmod +x scripts/test_retry.sh
./scripts/test_retry.sh
```

**Demonstrates:**

1. **Transient failure recovery**: 503 errors trigger retries
2. **Exponential backoff**: ~1s, ~2s, ~4s delays
3. **Jitter**: Random 0-1s added to prevent thundering herd
4. **Rate limiting**: 429 errors handled gracefully
5. **Max attempts**: Stops after 3 attempts

**Expected output:**

```
Phase 1: Transient failures (50% rate, retry recovers most)
Phase 2: Rate limiting (70% failure, backoff respects limits)
Phase 3: Exponential backoff (100% failures, observe timing)
Phase 4: Quick recovery (30% failures, fast retry success)
Retry pattern working correctly
```

#### Test 3: Combined Patterns

```sh
chmod +x scripts/test_resilience_patterns.sh
./scripts/test_resilience_patterns.sh
```

**Demonstrates:**

- Retry handles transient errors (503, 429)
- Circuit breaker handles systemic errors (500, connection refused)
- Pattern separation prevents inappropriate retries
- Self-healing system under various failure modes

### Part C: Chaos Engineering Experiment

Validates system resilience under **complete backend failure**:

```sh
chmod +x scripts/chaos_experiment.sh
./scripts/chaos_experiment.sh
```

**What it does:**

1. Establishes steady state baseline
2. Scales backend to 0 replicas (simulates pod crash)
3. Observes circuit breaker opening
4. Verifies fast-fail behavior
5. Restores backend (scales to 1 replica)
6. Observes automatic recovery
7. Verifies system health restoration

**Expected timeline:**

```
T+00s: Steady state verified
T+20s: Backend pods terminated
T+25s: Circuit breaker OPENS (5 failures detected)
T+25-60s: Fast-fail mode (<10ms responses)
T+60s: Backend restored
T+75s: Circuit HALF-OPEN, test call
T+77s: Circuit CLOSED, normal operation
T+90s: Full recovery verified
```

**Key metrics:**

- Client availability: **100%** (never crashed)
- Detection time: **5 seconds**
- Fast-fail response: **<10ms** (vs 30s timeout)
- Recovery time: **37 seconds** (automatic, no manual intervention)

### Advanced: Multi-Terminal Chaos Testing

For deeper observation, run chaos experiment with live monitoring:

**Terminal 1 - Watch logs:**

```sh
kubectl logs -l app=client-service -f
```

**Terminal 2 - Generate load:**

```sh
kubectl port-forward svc/client-service 9090:9090 &
./scripts/load_generator.sh http://localhost:9090 1
```

**Terminal 3 - Execute chaos:**

```sh
./scripts/chaos_experiment.sh
```

Watch Terminal 1 for the complete state transition sequence:

```log
[INFO] Request succeeded
[ERROR] Connection refused → retry_attempt: 1
[ERROR] Connection refused → circuit_breaker_failure_count: 5
[ERROR] circuit_breaker_opened
[ERROR] circuit_breaker_open: Fast-failing
[INFO] circuit_breaker_half_open: Testing recovery
[INFO] circuit_breaker_closed: Service recovered
[INFO] Request succeeded
```

### Chaos Toolkit (Alternative)

For automated chaos experiments with reporting:

```sh
# Install Chaos Toolkit
pip install chaostoolkit chaostoolkit-kubernetes

# Run experiment
chaos run chaos/backend-pod-deletion.json
```

This generates a detailed experiment report with steady-state validation and automatic rollback.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines for Python code
- Add type hints to all function signatures
- Include docstrings for public methods
- Write tests for new resilience patterns
- Update documentation for configuration changes
- Run all test suites before submitting PR

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->

## Contact

Vijeth P H - [@vijethph](https://github.com/vijethph)

Project Link: [https://github.com/vijethph/college-assignments](https://github.com/vijethph/college-assignments)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->

## Acknowledgments

Resources and inspirations that made this project possible:

- **Distributed Systems Principles**

  - [Principles of Chaos Engineering](https://principlesofchaos.org/) - Core chaos engineering methodology
  - [CAP Theorem](https://en.wikipedia.org/wiki/CAP_theorem) - Trade-offs in distributed systems
  - [Fallacies of Distributed Computing](https://en.wikipedia.org/wiki/Fallacies_of_distributed_computing) - Common misconceptions

- **Resilience Patterns**

  - [Netflix Hystrix](https://github.com/Netflix/Hystrix) - Circuit breaker pattern inspiration
  - [AWS Architecture Blog: Exponential Backoff And Jitter](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/) - Retry strategy best practices
  - [Microsoft Cloud Design Patterns](https://docs.microsoft.com/en-us/azure/architecture/patterns/) - Comprehensive pattern catalog

- **Tools & Libraries**

  - [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
  - [Tenacity](https://tenacity.readthedocs.io/) - Retry library
  - [Chaos Toolkit](https://chaostoolkit.org/) - Chaos engineering platform
  - [Kubernetes Documentation](https://kubernetes.io/docs/) - Container orchestration
  - [structlog](https://www.structlog.org/) - Structured logging

- **Learning Resources**

  - [Designing Data-Intensive Applications](https://dataintensive.net/) by Martin Kleppmann
  - [Release It!](https://pragprog.com/titles/mnee2/release-it-second-edition/) by Michael Nygard
  - [Site Reliability Engineering](https://sre.google/books/) by Google

- **README Template**
  - [Best-README-Template](https://github.com/othneildrew/Best-README-Template) - This README structure

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CLEANUP -->

## Cleanup

To remove all Kubernetes resources and clean up your environment:

```sh
chmod +x scripts/cleanup.sh
./scripts/cleanup.sh
```

This will:

- Delete all deployments
- Delete all services
- Clean up any lingering pods
- Stop port-forwards

To completely reset:

```sh
# Clean up Kubernetes resources
./scripts/cleanup.sh

# Stop Minikube
minikube stop

# (Optional) Delete Minikube cluster
minikube delete
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->

[contributors-shield]: https://img.shields.io/github/contributors/vijethph/college-assignments.svg?style=for-the-badge
[contributors-url]: https://github.com/vijethph/college-assignments/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/vijethph/college-assignments.svg?style=for-the-badge
[forks-url]: https://github.com/vijethph/college-assignments/network/members
[stars-shield]: https://img.shields.io/github/stars/vijethph/college-assignments.svg?style=for-the-badge
[stars-url]: https://github.com/vijethph/college-assignments/stargazers
[issues-shield]: https://img.shields.io/github/issues/vijethph/college-assignments.svg?style=for-the-badge
[issues-url]: https://github.com/vijethph/college-assignments/issues
[license-shield]: https://img.shields.io/github/license/vijethph/college-assignments.svg?style=for-the-badge
[license-url]: https://github.com/vijethph/college-assignments/blob/master/LICENSE.txt
[Python.org]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://python.org
[FastAPI.tiangolo.com]: https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white
[FastAPI-url]: https://fastapi.tiangolo.com
[Kubernetes.io]: https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white
[Kubernetes-url]: https://kubernetes.io
[Docker.com]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[Docker-url]: https://docker.com
