odoo.define("gastos_tqc.restrict_list_view",function(require){
    "use strict";
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var ListRender = require('web.ListRenderer');
    var _t = core._t;

    var ListRenderController = ListRender.include({
        /*Controlar lista en ciertos luegares*/
        _renderBody: function () {
            console.log("GAAAAAAAAA ES : ",this.model)
            var self = this;
            var $rows = this._renderRows();
            while ($rows.length < 4) {
                $rows.push(self._renderEmptyRow());
            }
            return $('<tbody>').append($rows);
        },
        _renderRow: function (record) {

            var self = this;
            var $cells = this.columns.map(function (node, index) {
                return self._renderBodyCell(record, node, index, { mode: 'readonly' });
            });
             /*Falta regla de estado mostrar*/
            if(record.model === "tqc.detalle.liquidaciones" && record.data.tipo === 'qwe')
            {
                var $tr = $('<tr/>', { class: 'o_data_row hide_row_gasto' })
                .attr('data-id', record.id)
                .append($cells);
            }else{
                var $tr = $('<tr/>', { class: 'o_data_row' })
                .attr('data-id', record.id)
                .append($cells);
            }

            if (this.hasSelectors) {
                $tr.prepend(this._renderSelector('td', !record.res_id));
            }
            this._setDecorationClasses($tr, this.rowDecorations, record);
            return $tr;
        },
        _renderRows: function () {
            // console.log('Este es el valor : ',this.value)
            // console.log('Este el modo : ',this.mode)
            console.log(this.model)
            console.log(this.res_id)
            console.log("MODELOS ES : ",this.model)
            console.log("STATE : ",this.state.model)
            return this.state.data.map(this._renderRow.bind(this));
        },
    })
    return ListRenderController
})