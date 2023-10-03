/**@odoo-module */
const { Component, onMounted, useState } = owl;
import { registry } from "@web/core/registry";
const actionRegistry = registry.category("actions");
const rpc = require('web.rpc');
export class EmployeeDashboard extends Component {
    setup(){
        super.setup(...arguments);
        console.log("vamos")
    }
}
actionRegistry.add("js_function", EmployeeDashboard);