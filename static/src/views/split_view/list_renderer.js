/** @odoo-module **/
const {useState, useChildSubEnv, useExternalListener, onMounted} = owl;

import {ListRenderer} from '@web/views/list/list_renderer';
import {registry} from "@web/core/registry";
import {listView} from "@web/views/list/list_view";
import {patch} from '@web/core/utils/patch';
import {useService} from '@web/core/utils/hooks';
import {SideFormviewContainer} from './side_form_view_container';
import {sideFormBeforeChangeFunctions} from "./hooks";
import {HeaderFlujo} from '@gastos_tqc/views/header_flujo';

// import {HeaderFlujoRenderer} from "../../../gastos_tqc/static/src/views/header_registry";

export class SplitViewRenderer extends ListRenderer {
    setup() {
        super.setup();
        // this._super.apply(this, arguments);
        this.actionService = useService('action');
        this.viewService = useService('view');
        this.userService = useService('user');

        this.sideFormView = useState({
            show: false,
            id: 0,
        })

        this.headerFlujoView = useState({
            show: this.props.list.model.env.searchModel.globalContext.mode_view === 'flujo',
        })

        const formViewId = this.getFormViewId()
        // console.log("form view : ", this)
        console.log("form view : ", this.props.list.model.env.searchModel.globalContext.mode_view)
        useChildSubEnv({
            config: {
                ...this.env.config,
                isX2Many: this.isX2Many,
                views: [[formViewId, 'form']],
                close: this.closeSideFormview.bind(this),
            },
        });

        onMounted(() => {
            // do something here
            console.log("super this : ", this)
            // console.log("super this : ", this.prop.list.model.env.searchModel.globalContext.mode_view)
            console.log("super this : ", this.props.list.model.env.searchModel._context.mode_view)
        });

        useExternalListener(window, 'keyup', this._onKeyUp.bind(this));
    }


    _onKeyUp(ev) {
        if (this.sideFormView.show && ev.code === 'Escape') {
            this.closeSideFormview();
        }
    }

    getFormViewId() {
        return this.env.config.views.find(view => view[1] === 'form')?.[0] || false
    }

    getSideFormViewContainerProps() {
        // console.log("this.props.list.resModel : ", this.props.list.resModel)
        // console.log("this.sideFormView.id : ", this.sideFormView.id)
        // console.log("this.sideFormViewRecord : ", this.sideFormViewRecord)

        const props = {
            resModel: this.props.list.resModel,
            resId: this.sideFormView.id,
            context: {
                ...this.sideFormViewRecord.context,
            },
            record: this.sideFormViewRecord,
        }
        const viewId = this.getFormViewId()
        if (viewId) {
            props.viewId = viewId
        }
        return props
    }

    async callSideFormBeforeChangeFunctions() {
        return await Promise.all(sideFormBeforeChangeFunctions.map(func => func()))
    }

    async onCellClicked(record, column, ev) {

        // si record.data.saldo es menor a 0, no hacer nada
        if (record.data.saldo < 0) {
            return;
        }
        // Agregar clase al elemento padre clickeado
        const element = ev.target.closest('td')
        const focusRow = this.tableRef.el.querySelector(`[data-id='${this.recordDatapointID}']`);
        // quitarle la clase o_list_record_selected a focusRow
        if (focusRow) {
            focusRow.classList.remove('o_list_record_selected')

        }
        if (element) {
            element.parentElement.classList.add('o_list_record_selected');
            // capturar elemento que tenga data-id igual datapint_6


            // element.classList.add('o_list_record_selected')
        }

        // if (
        //     (!this.isX2Many && !this.env.splitView?.enabled)
        //     || (this.isX2Many && !this.props.archInfo.splitView)
        // ) {
        //     console.log("Env. : ", this.env.splitView?.enabled)
        //     this._super.apply(this, arguments);
        //     return;
        // }
        if (ev.target.special_click) {
            console.log("gopp")
            return;
        }

        if (record.resId && this.sideFormView.id !== record.resId) {
            await this.callSideFormBeforeChangeFunctions();
            this.sideFormView.id = record.resId;
            this.sideFormView.show = true;
            this.sideFormViewRecord = record;
            this.recordDatapointID = record.id;
        }
    }

    async closeSideFormview() {
        await this.callSideFormBeforeChangeFunctions();
        this.sideFormView.show = false;
        this.sideFormView.id = false;
        this.keepFocusRow()
    }

    keepFocusRow() {
        this.tableRef.el.querySelector('tbody').classList.add('o_keyboard_navigation');
        const focusRow = this.tableRef.el.querySelector(`[data-id='${this.recordDatapointID}']`);
        focusRow.focus();
        // agregar clase a focusRow
    }
}


SplitViewRenderer.template = 'gastos_tqc.ListRenderer';
SplitViewRenderer.components = Object.assign({}, ListRenderer.components, {HeaderFlujo, SideFormviewContainer})

export const NewListView = {
    ...listView,
    Renderer: SplitViewRenderer,
}

registry.category("views").add("split_views", NewListView);
