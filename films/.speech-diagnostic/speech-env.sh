# Use the existing authorized Codex proxy for secure WebSockets.
# Does not alter the network allowlist or disable TLS validation.
if [ -n "${HTTPS_PROXY:-}" ]; then export WSS_PROXY="$HTTPS_PROXY"; fi
