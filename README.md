# pygdo-websocket

Websocket Connector for the [pygdo](https://github.com/gizmore/pygdo) application framework.

The module setting `ws_mira_comment_commands` defaults to off. When enabled,
WebSocket commands still run normally and are also forwarded to Mira for
commentary, subject to Mira's existing per-user opt-out. Command contents are
therefore shared with Mira; enable this only where that is appropriate.
