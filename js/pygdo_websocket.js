"use strict"


window.gdo.ws = {

    ws: null,
    tls: 0,
    autoconnect: 0,
    connecting: null,
    proto: null,

    load: function() {
        window.gdo.fetch('websocket', 'protocol').then(function(data) {
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
        const proto = window.gdo.ws.tls ? 'wss' : 'ws';
//        const wsUri = proto + "://" + window.gdo.ws.ip + ":" + window.gdo.ws.port + "/";
        const wsUri = proto + "://" + "py.giz.org:" + window.gdo.ws.port;
        const ws = window.gdo.ws.ws = new WebSocket(wsUri);
        ws.addEventListener("open", () => {
            if(window.gdo.ws.connecting) {
                clearTimeout(window.gdo.ws.connecting);
            }
            window.gdo.ws.connecting = null;
            window.gdo.ws.sendAuth();
        });
        ws.addEventListener("close", () => {
            window.gdo.ws.ws = null;
            window.gdo.ws.connect();
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
    sendAuth: function() {
        window.gdo.ws.send(window.gdo.ws.cookie);
    },
    send: function(data) {
        let log = document.getElementById('ws_log');
        if(log) {
            log.innerText += " > "
            log.innerText += data;
            log.innerText += "\n";
        }
        window.gdo.ws.ws.send(data);
    },

};

document.addEventListener('DOMContentLoaded', window.gdo.ws.load);
