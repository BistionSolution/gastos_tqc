odoo.define("gastos_tqc.js_table_depositos",function(require){
    "use strict";
    var AbtractAction = require("web.AbstractAction");
    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var field_registry = require('web.field_registry');
    var Dialog = require('web.Dialog');

    var WidgetTableDeposito = AbstractField.extend({
        template:"table_depositos",
        supportedFieldTypes:['html'],
        init:function (parent, name, record, options) {
            this._super(parent, name, record, options)
            // console.log('Este es el valor : ',this.value)
            // console.log('Este el modo : ',this.mode)
            // console.log(this.model)
            // console.log(this.res_id)
            // console.log(this.recordData.treatment_id)
            this.vali = "jajajaa";
        },
        start:function () {
            return this._super.apply(this, arguments);
            // this._drawTeeth()
        },
        isSet: function () {
            return true;
        },
        // _renderEdit:function () {
        //     console.log("render function agaaa")
        //     var self = this
        //
        // },
        _render : function ()
        {
            this._super.apply (this, arguments);
        },
        _renderReadonly: function () {
            console.log("RENDER READONLY")
        }
    })

    field_registry.add("widget_depositos",WidgetTableDeposito);

    return WidgetTableDeposito;
});