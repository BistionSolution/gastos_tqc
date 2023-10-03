/** @odoo-module **/

import {registry} from "@web/core/registry";
// import {listView} from "@web/views/list/list_view";
// import {ListRenderer} from "@web/views/list/list_renderer";
// import { HeaderFlujo } from "./header_flujo";
// import {HeaderFlujo} from '@gastos_tqc/views/header_flujo';
import {NewListView} from "@gastos_tqc/views/split_view/list_renderer";


// actualizar valor de estado headerFlujoView del componente NewListView
// NewListView.components.headerFlujoView.show = true


registry.category("views").add("header_gastos_approve", NewListView);


