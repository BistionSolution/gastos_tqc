odoo.define("gastos_tqc.restrict_editable_view", function (require) {
    "use strict";
    var core = require('web.core');
    var dom = require('web.dom');
    var ListRenderer = require('web.ListRenderer');
    var utils = require('web.utils');
    const {WidgetAdapterMixin} = require('web.OwlCompatibility');
    var _t = core._t;
    var session = require('web.session');

    var Dialog = require('web.Dialog');
    var view_dialogs = require('web.view_dialogs');

    ListRenderer.include({
        init: function (parent, state, params) {
            this._super.apply(this, arguments);
        },
        setRowMode: function (recordID, mode) {
            // Cambios agregado para quitar clase
            this.$('.o_selected_row').removeClass('hide_row_gasto');
            return this._super.apply(this, arguments);
        },
        _renderRow: function (record, index) {
            var $row = this._super.apply(this, arguments);
            if (record.model === "tqc.detalle.liquidaciones") {
                session.user_has_group('gastos_tqc.res_groups_aprobador_gastos').then(function (has_group) {
                    if (has_group) {
                        $row.find("td:last").remove();
                    }
                });
            }
            return $row
        },

    })
})