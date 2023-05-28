odoo.define("gastos_tqc.restrict_list_view", function (require) {
    "use strict";
    var ListRender = require('web.ListRenderer');

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
        // _renderRow: function (record) {
        //     var $row = this._super.apply(this, arguments);
        //     if (record.model === "tqc.detalle.liquidaciones" && record.data.state === 'historial') {
        //         console.log("record es : ",record.context.mode_view)
        //         if (record.context.mode_view !== 'flujo') {
        //             $row.addClass('hide_row_gasto')
        //         }
        //     }
        //     return $row;
        // },
    });
});