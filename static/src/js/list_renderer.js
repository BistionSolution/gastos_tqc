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
        start: function () {
            return this._super();
        },
        willStart: function () {
            return this._super.apply(this, arguments);
        },
        destroy: function () {

            return this._super.apply(this, arguments);
        },
        on_attach_callback: function () {
            this.isInDOM = true;
            this._super();
            // _freezeColumnWidths requests style information, which produces a
            // repaint, so we call it after _super to prevent flickering (in case
            // other code would also modify the DOM post rendering/before repaint)
            this._freezeColumnWidths();
        },
        _renderBody: function () {
            // console.log("GAAAAAAAAA ES : ",this.model)
            var self = this;
            var $rows = this._renderRows();
            while ($rows.length < 4) {
                $rows.push(self._renderEmptyRow());
            }
            return $('<tbody>').append($rows);
        },
        /**
         * Render a row, corresponding to a record.
         *
         * @private
         * @param {Object} record
         * @returns {jQueryElement} a <tr> element
         */
        _renderRow: function (record,index) {
            console.log("Index 222 : ",index)
            var $row = this._super.apply(this, arguments);
            console.log("RENDER ROW : ",$row)
            if(record.model === "tqc.detalle.liquidaciones" && record.data.tipo === 'qwe')
            {
                $row.addClass('hide_row_gasto')
            }
            return $row;
        },
        _renderRows: function () {
            console.log("ALL FILA")
            return this._super.apply(this, arguments);
        },
    });
    return MyListRenderer;
});