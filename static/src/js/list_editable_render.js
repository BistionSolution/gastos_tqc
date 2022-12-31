odoo.define("gastos_tqc.restrict_editable_view",function(require){
    "use strict";
    var core = require('web.core');
    var dom = require('web.dom');
    var ListRenderer = require('web.ListRenderer');
    var utils = require('web.utils');
    const { WidgetAdapterMixin } = require('web.OwlCompatibility');
    var _t = core._t;

    var ListEditableRender = ListRenderer.include({
        setRowMode: function (recordID, mode) {
            var self = this;
            var record = self._getRecord(recordID);
            if (!record) {
                return Promise.resolve();
            }

            var editMode = (mode === 'edit');
            var $row = this._getRow(recordID);
            this.currentRow = editMode ? $row.prop('rowIndex') - 1 : null;
            var $tds = $row.children('.o_data_cell');
            var oldWidgets = _.clone(this.allFieldWidgets[record.id]);

            // Prepare options for cell rendering (this depends on the mode)
            var options = {
                renderInvisible: editMode,
                renderWidgets: editMode,
            };
            options.mode = editMode ? 'edit' : 'readonly';

            // Switch each cell to the new mode; note: the '_renderBodyCell'
            // function might fill the 'this.defs' variables with multiple promise
            // so we create the array and delete it after the rendering.
            var defs = [];
            this.defs = defs;
            _.each(this.columns, function (node, colIndex) {
                var $td = $tds.eq(colIndex);
                var $newTd = self._renderBodyCell(record, node, colIndex, options);

                // Widgets are unregistered of modifiers data when they are
                // destroyed. This is not the case for simple buttons so we have to
                // do it here.
                if ($td.hasClass('o_list_button')) {
                    self._unregisterModifiersElement(node, recordID, $td.children());
                }

                // For edit mode we only replace the content of the cell with its
                // new content (invisible fields, editable fields, ...).
                // For readonly mode, we replace the whole cell so that the
                // dimensions of the cell are not forced anymore.
                if (editMode) {
                    $td.empty().append($newTd.contents());
                } else {
                    self._unregisterModifiersElement(node, recordID, $td);
                    $td.replaceWith($newTd);
                }
            });
            delete this.defs;

            // Destroy old field widgets
            _.each(oldWidgets, this._destroyFieldWidget.bind(this, recordID));

            // Toggle selected class here so that style is applied at the end
            $row.toggleClass('o_selected_row', editMode);
            // Cambios agregado para quitar clase
            console.log("edit liquidacioness")
            this.$('.o_selected_row').removeClass('hide_row_gasto');
            if (editMode) {
                this._disableRecordSelectors();
            } else {
                this._enableRecordSelectors();
            }

            return Promise.all(defs).then(function () {
                // mark Owl sub components as mounted
                WidgetAdapterMixin.on_attach_callback.call(self);

                // necessary to trigger resize on fieldtexts
                core.bus.trigger('DOM_updated');
            });
        },
    })
})