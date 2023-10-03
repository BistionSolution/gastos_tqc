/** @odoo-module */

import {archParseBoolean} from '@web/views/utils';

import {ListArchParser} from '@web/views/list/list_arch_parser';

import {patch} from '@web/core/utils/patch';

patch(ListArchParser.prototype, 'gastos_tqc', {
    parse(arch, models, modelName) {
        const result = this._super.apply(this, arguments);
        const xmlDoc = this.parseXML(arch);
        result.splitView = archParseBoolean(xmlDoc.getAttribute('split_view') || '');
        return result
    }
})