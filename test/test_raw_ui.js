const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {test} = require('node:test');

test('form submission sends once, retaining commands while disconnected', () => {
    let onSubmit;
    const form = {dataset: {}, addEventListener: (name, handler) => {
        assert.equal(name, 'submit'); onSubmit = handler;
    }};
    const line = {form, value: '$servers'};
    const output = [];
    const log = {appendChild: node => output.push(node)};
    const socket = {readyState: 1, send: text => output.push('sent:' + text)};
    const document = {
        getElementById: id => id === 'ws_cmdline' ? line : id === 'ws_log' ? log : null,
        createTextNode: text => text,
    };
    const window = {gdo: {}};
    const context = {window, document, console, WebSocket: {OPEN: 1, CONNECTING: 0}};
    context.gdo = window.gdo;
    vm.runInNewContext(fs.readFileSync('gdo/websocket/js/pygdo_websocket.js', 'utf8'), context);
    window.gdo.ws.ws = socket;
    window.gdo.ws.init();
    let prevented = false;
    onSubmit({preventDefault: () => { prevented = true; }});
    assert.equal(prevented, true);
    assert.equal(line.value, '');
    assert.deepEqual(output, ['sent:$servers', ' > $servers\n']);
    line.value = 'hello duck';
    onSubmit({preventDefault() {}});
    assert.equal(output.at(-2), 'sent:hello duck');
    line.value = '$help';
    socket.readyState = 3;
    onSubmit({preventDefault() {}});
    assert.equal(line.value, '$help');
    assert.match(output.at(-1), /not sent/);
});
