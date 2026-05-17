# Multi-Device Hub Implementation Plan

## Goal
Transform the integration to use a hub-and-spoke model where one integration entry creates a hub with multiple child devices.

## Current vs New Architecture

### Current (v1.0.5)
```
Integration Entry: "9Router - Claude (Auth: 0)"
└── Device: "Claude (Auth 0)"
    └── Sensor: "Claude Quota"

Integration Entry: "9Router - Codex (Auth: 0)"
└── Device: "Codex (Auth 0)"
    └── Sensor: "Codex Quota"
```

### New (v2.0.0)
```
Integration Entry: "9Router (192.168.1.107)"
└── Hub Device: "9Router"
    ├── Device: "Claude - BIMLOGiQ"
    │   └── Sensor: "Claude BIMLOGiQ Quota"
    ├── Device: "Codex - tienanhthananh4680"
    │   └── Sensor: "Codex tienanhthananh4680 Quota"
    └── Device: "Trouter 1"
        └── Sensor: "Trouter 1 Quota"
```

## Implementation Steps

### 1. Update Config Flow
- Remove provider and auth_index fields
- Only ask for: Data Source, Base URL, Password (if needed)
- Entry title: "{Data Source} ({URL})"

### 2. Update Coordinator
- Fetch ALL connections/accounts
- Store data for all accounts
- Return dict keyed by connection ID

### 3. Update Sensor Platform
- Create hub device
- Discover all connections
- Create one device + sensor per connection
- Use connection ID as unique identifier

### 4. Device Info Structure
```python
# Hub device
DeviceInfo(
    identifiers={(DOMAIN, f"{data_source}_{base_url_hash}")},
    name=f"{data_source_name}",
    manufacturer="AI Quota",
    model=data_source_name,
)

# Child device
DeviceInfo(
    identifiers={(DOMAIN, f"{data_source}_{connection_id}")},
    name=f"{provider} - {account_name}",
    manufacturer="AI Quota",
    model=plan,
    via_device=(DOMAIN, f"{data_source}_{base_url_hash}"),  # Link to hub
)
```
