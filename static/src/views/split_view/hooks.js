/** @odoo-module **/

export const sideFormBeforeChangeFunctions = []

export function onSideFormBeforeChange(func) {
    sideFormBeforeChangeFunctions.push(func)
}