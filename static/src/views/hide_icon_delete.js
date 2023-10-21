/** @odoo-module **/
import {patch} from "@web/core/utils/patch";
import {ListRenderer} from "@web/views/list/list_renderer";
import {X2ManyField} from "@web/views/fields/x2many/x2many_field";
import session from 'web.session';
// import {listView} from "@web/views/list/list_view"
// import {ListController} from "@web/views/list/list_controller";
import {registry} from "@web/core/registry";
import {TestX2ManyField} from "./one2many_selectable";
import rpc from 'web.rpc';

const {onWillStart, onWillUpdateProps, useState} = owl;
// const {Component, onWillStart, onRendered, onMounted} = owl;

// patch(ListRenderer.prototype, "my_list_view_patch", {
//     // Define the patched method here
//     setup() {
//         console.log("List view started!");
//         this._super.apply(this, arguments);
//
//         // Call the new method
//         // this.myNewMethod();
//     },
//
//     // Define a new method
//     _onClick() {
//         console.log(this.hasX2ManyAction)
//         this.hasX2ManyAction = false
//     },
// });
// class MyListRender extends ListRenderer {
//     setup() {
//         super.setup(...arguments);
//         console.log("List controller started! no se que pasa");
//     }
// }
//
// MyListRender.recordRowTemplate = 'owl_learn.ClickMe.RecordRow';
//
// registry.category("fields").add("my_list_renderer", MyListRender);

export class TestListRenderer extends ListRenderer {

    setup() {
        super.setup();
        // session.user_has_group('gastos_tqc.res_groups_aprobador_gastos').then(function (has_group) {
        //     console.log("entro xd")
        //     if (has_group) {
        //
        //     }
        // });
        this.showRemoveIcon = useState({value: false});
        onWillStart(() => this._loadPro());
    }

    get hasSelectors() {
        const dataRecord = this.props.list.model.root.data
        if ((dataRecord.state === 'jefatura' && dataRecord.uid_create === 3 && dataRecord.current_user === 1) || (dataRecord.state === 'contable' && dataRecord.uid_create === 2)) {
            this.props.allowSelectors = true
            let list = this.props.list
            list.selection = list.records.filter((rec) => rec.selected)
            list.selectDomain = (value) => {
                list.isDomainSelected = value;
                list.model.notify();
            }
        }

        return this.props.allowSelectors && !this.env.isSmall;
    }

    async _loadPro() {
        if (await session.user_has_group('gastos_tqc.res_groups_administrator')) {
            this.showRemoveIcon.value = false
        }
        if (await session.user_has_group('gastos_tqc.res_groups_aprobador_gastos')) {
            this.showRemoveIcon.value = false
        }
    }
}

TestListRenderer.recordRowTemplate = 'owl_learn.ClickMe.RecordRow';

export class NewListRenderer extends X2ManyField {
    setup() {
        super.setup();
        this.showModalDescription = useState({value: false});
        this.descriptionRechazo = useState({text: ''});

    }

    get hasSelected() {
        return this.list.records.filter((rec) => rec.selected).length
    }

    async deleteSelected() {
        // Obtener valor de campo state del registro padre
        this.descriptionRechazo.text = ''
        this.showModalDescription.value = true
    }

    async _onClickAceptar() {
        const state = this.props.record.data.state
        var current_model = this.field.relation;
        let selected = this.list.records.filter((rec) => rec.selected)
        this.list.records
        var selected_list = []
        selected.forEach((rec) => {
            if (rec.data.id) {
                selected_list.push(parseInt(rec.data.id))
            } else {
                if (this.activeActions.onDelete) {
                    selected.forEach((rec) => {
                        this.activeActions.onDelete(rec);
                    })
                }

            }
        })
        var self = this;
        if (selected_list.length != 0) {
            // this.showModalDescription.value = true
            var response = await rpc.query({
                model: current_model,
                method: 'write',
                args: [selected_list, {
                    'revisado_state': 'rechazado_' + state,
                    [state === 'contable' ? 'observacioncontabilidad' : 'observacionjefatura']: this.descriptionRechazo.text
                }],
            }).then(function (response) {
                self.rendererProps.list.model.load()
            });
        }
        this.showModalDescription.value = false
    }

    async restaurarRecord() {
        // Obtener valor de campo state del registro padre
        const state = this.props.record.data.state
        var current_model = this.field.relation;
        let selected = this.list.records.filter((rec) => rec.selected)
        this.list.records
        var selected_list = []
        selected.forEach((rec) => {
            if (rec.data.id) {
                selected_list.push(parseInt(rec.data.id))
            } else {
                if (this.activeActions.onDelete) {
                    selected.forEach((rec) => {
                        this.activeActions.onDelete(rec);
                    })
                }

            }
        })
        var self = this;
        if (selected_list.length != 0) {
            // this.showModalDescription.value = true
            var response = await rpc.query({
                model: current_model,
                method: 'write',
                args: [selected_list, {
                    'revisado_state': 'borrador'
                }],
            }).then(function (response) {
                self.rendererProps.list.model.load()
            });
        }
    }

    _onClickClose() {
        this.showModalDescription.value = false
    }
}

// export const newListView = {
//     ...listView,
//     Renderer: NewListRenderer,
// }
NewListRenderer.components = {
    ...X2ManyField.components, ListRenderer: TestListRenderer
}
NewListRenderer.template = "one2many_mass_select_delete.One2manyDelete";
// newListView.Renderer.recordRowTemplate = 'owl_learn.ClickMe.RecordRow';

registry.category("fields").add("icon_delete", NewListRenderer);