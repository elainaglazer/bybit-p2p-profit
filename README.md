(vibe code the whole thing)


# Bybit P2P Arbitrage Monitor

A simple Python script to monitor Bybit P2P prices for USDT/VND and alert on profitable spreads.

## Setup

1.  **Install Python**: Make sure Python is installed on your system.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Running

*   **Windows**: Double-click `run_monitor.bat`.
*   **Terminal**:
    ```bash
    python bybit_p2p_monitor.py
    ```

## Configuration

Edit `bybit_p2p_monitor.py` to change:
*   `THRESHOLD`: Minimum profit spread to alert (default: 200 VND).
*   `CAPITAL`: Amount of VND to trade (default: 5,500,000 VND).
*   `CHECK_INTERVAL`: How often to check (default: 60 seconds).
