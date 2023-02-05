odoo.define("gastos_tqc.restrict_list_view", function (require) {
    "use strict";
    var BasicRenderer = require('web.BasicRenderer');
    const {ComponentWrapper} = require('web.OwlCompatibility');
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

    ListRender.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
            // this.$current.delegate('td', 'click', function (e) {
            //     console.log("HOLA")
            //
            //     e.stopPropagation();
            // });
        },
        _render: function () {
            this.$el.addClass('o_list_gastos')
            return this._super.apply(this, arguments);
        },
        willStart: function () {
            return this._super.apply(this, arguments);
        },
        _renderRow: function (record) {
            var self = this;
            var $row = this._super.apply(this, arguments);

            if (record.model === "tqc.detalle.liquidaciones" && record.data.state === 'historial') {
                if (record.context.mode_view !== 'flujo') {
                    $row.addClass('hide_row_gasto')
                }
            }
            return $row;
        },
        _renderRows: function () {
            return this._super.apply(this, arguments);
        },
    });
});