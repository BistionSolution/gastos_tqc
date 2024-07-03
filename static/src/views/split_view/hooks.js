/** @odoo-module **/

export const sideFormBeforeChangeFunctions = []

export function onSideFormBeforeChange(func) {
    sideFormBeforeChangeFunctions.push(func)
}

export function clearSideFormBeforeChangeFunctions() {
    sideFormBeforeChangeFunctions.length = 0
}
