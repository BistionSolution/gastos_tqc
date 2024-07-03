/** @odoo-module **/

import {ListController} from '@web/views/list/list_controller';
import {CheckBox} from '@web/core/checkbox/checkbox';

import {patch} from '@web/core/utils/patch';
import {onWillStart, EventBus, useSubEnv} from '@odoo/owl';

export const sideFormBus = new EventBus()

patch(ListController.prototype, 'web_listview_side_formview', {

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

        sideFormBus.addEventListener('on_save_side_formview', this.onBusSaveSideFormView.bind(this));
    },

    getLocalKeySplitView() {
        const model = this.props.resModel;
        return `sf_${model}`
    },

    onToggleSplitView(value) {
        const localKey = this.getLocalKeySplitView();
        localKey && localStorage.setItem(localKey, value);
        this.splitView.enabled = value;
    },

    async onBusSaveSideFormView(payload) {
        const {record, params} = payload.detail;
        this.onSaveSideFormView(record, params)
    },

    async onSaveSideFormView(record, params) {
        const record2update = this.model.root.records.find(r => r.resId === record.resId && r.resModel === record.resModel)
        if (!record2update) return
        this.model.root.invalidateCache();
        await record2update.load();
        this.model.notify();
    },

})

ListController.components = {
    ...ListController.components,
    CheckBox,
};
