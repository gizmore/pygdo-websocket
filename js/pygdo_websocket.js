"use strict"
window.GDO.ws = {

    ws: null,
    tls: 0,
    autoconnect: 0,

    init: function() {
        debugger;
        const proto = window.GDO.ws.tls ? 'wss' : 'ws';
        const wsUri = proto + "://" + window.GDO.ws.ip + ":" + window.GDO.ws.port + "/";
        const ws = window.GDO.ws.ws = new WebSocket(wsUri);
        ws.addEventListener("open", () => {
            window.GDO.ws.sendAuth();
        });
        ws.addEventListener("error", (e) => {
            console.log(e)
        });
        ws.addEventListener("message", (e) => {
            log(`RECEIVED: ${e.data}`);
        });
    },
    sendAuth: function() {
        window.GDO.ws.send("HI!")
    },
    send: function(data) {
        window.GDO.ws.ws.send(JSON.stringify(data));
    },
};
