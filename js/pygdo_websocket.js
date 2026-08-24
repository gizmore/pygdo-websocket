"use strict"

window.gdo.ws = {

    ws: null,
    tls: 0,
    autoconnect: 0,
    connecting: null,
    proto: null,

    gdo_init: function() {
        window.gdo.fetch('websocket.protocol.json').then(function(data) {
            window.gdo.ws.init();
        });
    },

    init: function() {
        let submit = document.getElementById('gdo.websocket.method.raw.raw_submit');
        if(submit) {
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
        ws.addEventListener("close", () => {
            if (window.gdo.ws.ws === ws) {
                window.gdo.ws.ws = null;
                window.gdo.ws.connect();
            }
        });
        ws.addEventListener("message", (e) => {
            let log = document.getElementById('ws_log');
            if(log) {
                log.innerHTML += e.data;
                log.innerHTML += "\n";
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
            log.innerText += " > "
            log.innerText += data;
            log.innerText += "\n";
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
