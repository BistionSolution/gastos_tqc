odoo.define("gastos_tqc.form_view_restrict", function (require) {
    "use strict";
    var core = require('web.core');

    var Dialog = require('web.Dialog');
    var dialogs = require('web.view_dialogs');
    var FormController = require('web.FormController');
    var _t = core._t;
    var qweb = core.qweb;

    var restrictController = FormController.include({
        // SI DEVUELVE TRUE NO PUEDE ENTRAR
        init: function (parent, model, renderer, params) {
            this._super.apply(this, arguments);
            console.log(" estes cagd : ", this.initialState.data.id)
            this._rpc({
                model: "tqc.liquidaciones",
                method: "write",
                args: [this.initialState.data.id, { // Here 1 is id of record
                    "mode_view": "flujo"
                }],
            })
        },
    })
    return restrictController
})
