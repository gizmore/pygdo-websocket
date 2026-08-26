"use strict"

window.gdo.ws = {

    ws: null,
    tls: 0,
    autoconnect: 0,
    connecting: null,
    proto: null,

    appendLog: function(log, text) {
        if(log) {
            log.textContent += String(text).replace(/(?:\r\n|\r|\n)+$/, '') + "\n";
        }
    },

    appendRenderedLog: function(log, html) {
        if(log) {
            log.insertAdjacentHTML('beforeend', String(html).replace(/(?:\r\n|\r|\n)+$/, ''));
            log.appendChild(document.createTextNode("\n"));
        }
    },

    gdo_init: function() {
        if (!document.getElementById('ws_log')) {
            return;
        }
        window.gdo.fetch('websocket.protocol.json').then(function(data) {
            window.gdo.ws.init();
        });
    },

    init: function() {
        let submit = document.getElementById('gdo.websocket.method.raw.raw_submit');
        if(submit && !submit.dataset.gdoWebsocketBound) {
            submit.dataset.gdoWebsocketBound = '1';
            submit.addEventListener('click', function(e) {
                e.preventDefault();
                let line = document.getElementById('ws_cmdline');
                if(line) {
                    gdo.ws.send(line.value)
                    line.value = '';
                }
                return false;
            });
        }
        window.gdo.ws.connect();
    },

    connect: function() {
        const current = window.gdo.ws.ws;
        if (current && (current.readyState === WebSocket.CONNECTING || current.readyState === WebSocket.OPEN)) {
            return;
        }
        const proto = window.gdo.ws.tls ? 'wss' : 'ws';
        const wsUri = proto + "://" + window.gdo.ws.ip + ":" + window.gdo.ws.port;
        const ws = window.gdo.ws.ws = new WebSocket(wsUri);
        ws.addEventListener("open", () => {
            if(window.gdo.ws.connecting) {
                clearTimeout(window.gdo.ws.connecting);
            }
            window.gdo.ws.connecting = null;
            window.gdo.ws.sendAuth(ws);
        });
        ws.addEventListener("close", (event) => {
            if (window.gdo.ws.ws === ws) {
                window.gdo.ws.ws = null;
                if (event.code === 1008) {
                    console.warn('WebSocket authentication is required; reconnect disabled.');
                    return;
                }
                if (!window.gdo.ws.connecting) {
                    window.gdo.ws.connecting = setTimeout(() => {
                        window.gdo.ws.connecting = null;
                        window.gdo.ws.connect();
                    }, 60000);
                }
            }
        });
        ws.addEventListener("message", (e) => {
            let log = document.getElementById('ws_log');
            if(log) {
                window.gdo.ws.appendRenderedLog(log, e.data);
            } else {
                 console.log(e.data);
            }
        });
        ws.addEventListener("error", (e) => {
            console.error(e)
        });
    },
    sendAuth: function(ws) {
        window.gdo.ws.send(window.gdo.ws.cookie, ws);
    },
    send: function(data, ws) {
        let log = document.getElementById('ws_log');
        if(log) {
            window.gdo.ws.appendLog(log, " > " + data);
        }
        ws = ws || window.gdo.ws.ws;
        if (!ws || ws.readyState !== WebSocket.OPEN) {
            console.warn('WebSocket is not open; message was not sent.');
            return false;
        }
        ws.send(data);
        return true;
    },

};
