# DevOps WebSocket Protocol

## Overview

Real-time WebSocket protocol for the DevOps Engine. Allows the React frontend to receive live deployment updates without polling.

**Protocol Version:** `1.0`

---

## Connection

Connect to the WebSocket endpoint with a JWT token as a query parameter:

```
ws://localhost:8000/ws/deployments/<deployment_id>/?token=<jwt>
ws://localhost:8000/ws/projects/<project_id>/?token=<jwt>
ws://localhost:8000/ws/user/?token=<jwt>
```

If the token is valid, the server sends a `connection.established` event. If invalid, the connection is closed with code `4001`.

---

## Authentication

| Close Code | Meaning |
|-----------|---------|
| 4001 | Authentication failed (invalid/expired JWT) |
| 4003 | Not authorized for this channel |

---

## Routes

| Route | Consumer | Description |
|-------|----------|-------------|
| `ws/deployments/<deployment_id>/` | `DeploymentConsumer` | Real-time updates for a specific deployment |
| `ws/projects/<project_id>/` | `ProjectConsumer` | Updates for all deployments in a project |
| `ws/user/` | `UserConsumer` | User-specific notifications (requires auth) |

---

## Message Format

All messages (client and server) use JSON:

```json
{
  "version": "1.0",
  "event": "deployment.completed",
  "event_id": "550e8400-e29b-41d4-a716-446655440000",
  "deployment_id": "abc123",
  "correlation_id": "optional-id-from-phase-11",
  "timestamp": "2026-07-26T12:00:00Z",
  "payload": {}
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | Yes | Protocol version (`1.0`) |
| `event` | string | Yes | Event type identifier |
| `event_id` | string (UUID) | Yes | Unique event identifier |
| `timestamp` | string (ISO 8601) | Yes | Server timestamp |
| `payload` | object | Yes | Event-specific data |
| `deployment_id` | string | No | Deployment UUID (when applicable) |
| `correlation_id` | string | No | Propagated from Phase 11 |

---

## Heartbeat

The server sends a `pong` event every 30 seconds. Clients should respond with `{"action": "ping"}`.

**Client:**
```json
{"action": "ping"}
```

**Server:**
```json
{
  "version": "1.0",
  "event": "pong",
  "event_id": "...",
  "timestamp": "...",
  "payload": {}
}
```

---

## Client Actions

| Action | Description |
|--------|-------------|
| `ping` | Request a `pong` from the server |
| `subscribe.deployment` | Subscribe to a deployment (DeploymentConsumer only) |
| `unsubscribe.deployment` | Unsubscribe from a deployment |
| `subscribe.project` | Subscribe to a project (ProjectConsumer only) |
| `unsubscribe.project` | Unsubscribe from a project |
| `cancel.deployment` | Request cancellation of a deployment |

---

## Server Events

### Deployment Lifecycle

| Event | Payload |
|-------|---------|
| `deployment.queued` | `{deployment_id}` |
| `deployment.started` | `{deployment_id}` |
| `deployment.waiting` | `{deployment_id, reason}` |
| `deployment.completed` | `{deployment_id, status}` |
| `deployment.failed` | `{deployment_id, error}` |
| `deployment.cancelled` | `{deployment_id}` |
| `deployment.warning` | `{deployment_id, message}` |
| `deployment.info` | `{deployment_id, message}` |

### Stage Progress

| Event | Payload |
|-------|---------|
| `stage.started` | `{deployment_id, stage_name}` |
| `stage.completed` | `{deployment_id, stage_name}` |
| `progress.updated` | `{deployment_id, phase}` |

### Logs

| Event | Payload |
|-------|---------|
| `log.created` | `{deployment_id, level, message, stage}` |

### System

| Event | Payload |
|-------|---------|
| `connection.established` | `{deployment_id or project_id or user_id}` |
| `action.acknowledged` | `{action, data}` |
| `pong` | `{}` |
| `error` | `{message, code}` |

---

## Close Codes

| Code | Meaning |
|------|---------|
| 1000 | Normal closure |
| 1001 | Going away |
| 1002 | Protocol error |
| 4001 | Authentication failed |
| 4002 | Authentication expired |
| 4003 | Not authorized |

---

## React Example

```javascript
const token = getAccessToken();
const ws = new WebSocket(
  `ws://localhost:8000/ws/deployments/${deploymentId}/?token=${token}`
);

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);

  switch (msg.event) {
    case 'deployment.completed':
      console.log('Deployment done!', msg.payload);
      break;
    case 'deployment.failed':
      console.error('Deployment failed:', msg.payload.error);
      break;
    case 'progress.updated':
      console.log('Phase:', msg.payload.phase);
      break;
    case 'log.created':
      console.log(`[${msg.payload.level}] ${msg.payload.message}`);
      break;
    case 'pong':
      // heartbeat acknowledged
      break;
    case 'error':
      console.error('WS error:', msg.payload.message);
      break;
  }
};

// Heartbeat ping
setInterval(() => {
  ws.send(JSON.stringify({ action: 'ping' }));
}, 30000);
```
