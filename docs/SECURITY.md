# Security model

1. Keep all provider keys and API tokens in environment variables.
2. Protect non-health API endpoints with bearer authentication.
3. Register only explicitly authorized devices.
4. Expose only allowlisted tools; never add a generic command-execution endpoint.
5. Require explicit confirmation before sensitive device actions are introduced.
6. Encrypt remote transport and use a user-controlled private network for remote connectivity.
7. Record security-relevant actions in an append-only audit trail as the system grows.
8. Fail closed when a provider, device, or permission cannot be verified.
