odoo.define("gastos_tqc.js_table_depositos", function (require) {
    "use strict";
    var AbtractAction = require("web.AbstractAction");
    var AbstractField = require("web.AbstractField");
    var core = require("web.core");
    var Widget = require('web.Widget');
    var rpc = require('web.rpc');
    var field_registry = require('web.field_registry');
    var Dialog = require('web.Dialog');
    var QWeb = core.qweb;

    var WidgetTableDeposito = AbstractField.extend({
        // template: "gastos_tqc.table_depositos",
        supportedFieldTypes: ['html'],
        init: function (parent, name, record, options) {
            this._super(parent, name, record, options)
            // console.log('VER TABLA : ', this.value)
            // console.log('TABLA PRO : ', this.mode)
            // console.log(this.model)
            // console.log(this.res_id)
            // console.log(this.recordData)
            // this.vali = "jajajaa";
        },
        start: function () {
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
        _render: async function () {
            var self = this;
            await this._super(...arguments);
            const result = await this._rpc({
                model: 'tqc.detalle.liquidaciones',
                method: 'search_read',
                domain:[['liquidacion_id','=',self.res_id],['state','=','historial']],
            });
            console.log("RESULTADOS : ", result)
            const elem = QWeb.render('gastos_tqc.table_depositos', {
                expenses: result
            });
            console.log("ESTO element : ", self.$el)
            self.$el.html(elem);

            // var $row = this._super(record);
            // // Add progress bar widget at the end of rows
            // var $td = $('<td/>', {class: 'o_data_cell o_skill_cell'});
            // var progress = new FieldProgressBar(this, 'level_progress', record, {
            //     current_value: record.data.level_progress,
            //     attrs: this.arch.attrs,
            // });
            // progress.appendTo($td);
            // return $row.append($td);
        },
        _renderReadonly: function () {
            // console.log("RENDER READONLY")
        }
    })

    field_registry.add("widget_depositos", WidgetTableDeposito);

    return WidgetTableDeposito;
});