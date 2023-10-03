/** @odoo-module **/

import {ListController} from '@web/views/list/list_controller';
import {CheckBox} from '@web/core/checkbox/checkbox';

import {patch} from '@web/core/utils/patch';
import {onWillStart, useSubEnv} from '@odoo/owl';

patch(ListController.prototype, 'gastos_tqc', {

    setup() {
        this._super();

        this.splitView = {
            available: this.env.config.views.find(view => view[1] === 'list'),
            enabled: false,
        }
        useSubEnv({
            splitView: this.splitView,
        })

        onWillStart(async () => {
            const localKey = this.getLocalKeySplitView();
            const localValue = localKey && localStorage.getItem(localKey)
            this.splitView.enabled = localValue ? JSON.parse(localValue) : !!this.props.context.split_view;
        })
    },

    getLocalKeySplitView() {
        const model = this.props.resModel;
        return `sf_${model}`
    },

    onToggleSplitView(value) {
        const localKey = this.getLocalKeySplitView();
        localKey && localStorage.setItem(localKey, value);
        this.splitView.enabled = value;
    }

})

ListController.components = {
    ...ListController.components,
    CheckBox,
};