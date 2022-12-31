odoo.define("gastos_tqc.restrict_list_view",function(require){
    "use strict";
    var BasicRenderer = require('web.BasicRenderer');
    const { ComponentWrapper } = require('web.OwlCompatibility');
    var config = require('web.config');
    var core = require('web.core');
    var dom = require('web.dom');
    var ListRender = require('web.ListRenderer');
    var field_utils = require('web.field_utils');
    var Pager = require('web.Pager');
    var utils = require('web.utils');
    var viewUtils = require('web.viewUtils');
    var _t = core._t;

    var DECORATIONS = [
    'decoration-bf',
    'decoration-it',
    'decoration-danger',
    'decoration-info',
    'decoration-muted',
    'decoration-primary',
    'decoration-success',
    'decoration-warning'
    ];

    var FIELD_CLASSES = {
        char: 'o_list_char',
        float: 'o_list_number',
        integer: 'o_list_number',
        monetary: 'o_list_number',
        text: 'o_list_text',
        many2one: 'o_list_many2one',
    };

    var MyListRenderer = ListRender.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
        },
        willStart: function () {
            // console.log('ESte es el valor : ',this)
            console.log(this.model)
            console.log(this.res_id)
            console.log(this.recordData)
            return this._super.apply(this, arguments);
        },
        _renderRow: function (record) {
            console.log("Index 222 : ")
            var $row = this._super.apply(this, arguments);
            console.log("RENDER ROW : ",record.data.state)
            if(record.model === "tqc.detalle.liquidaciones" && record.data.state === 'historial')
            {
                $row.addClass('hide_row_gasto')
            }
            return $row;
        },
        _renderRows: function () {
            return this._super.apply(this, arguments);
        },
    });
    return MyListRenderer;
});