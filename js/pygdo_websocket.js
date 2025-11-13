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
        window.gdo.ws.connecting = setInterval(window.gdo.ws.connect, 5000);
        window.gdo.ws.connect();
    },

    connect: function() {
        const proto = window.gdo.ws.tls ? 'wss' : 'ws';
        const wsUri = proto + "://" + window.gdo.ws.ip + ":" + window.gdo.ws.port + "/";
        const ws = window.gdo.ws.ws = new WebSocket(wsUri);
        ws.addEventListener("open", () => {
            clearInterval(window.gdo.ws.connecting);
            window.gdo.ws.sendAuth();
        });
        ws.addEventListener("close", () => {
            window.gdo.ws.ws = null;
            window.gdo.ws.connecting = setInterval(window.gdo.ws.connect, 5000);
            window.gdo.ws.connect();
        });
        ws.addEventListener("message", (e) => {
            console.log(e);
        });
        ws.addEventListener("error", (e) => {
            console.error(e)
        });
    },
    sendAuth: function() {
        window.gdo.ws.send(window.gdo.ws.cookie);
    },
    send: function(data) {
        window.gdo.ws.ws.send(JSON.stringify(data));
    },
};

document.addEventListener('DOMContentLoaded', window.gdo.ws.load);
