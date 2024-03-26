from odoo import models, fields, api, _, Command


class ChangeBulkPasswordUser(models.TransientModel):

    _name = 'change.bulk.password.user'
    _description = 'User, Change Bulk Password'

    new_b_passwd = fields.Char(string='New Password', default='')

    def change_password_bulk(self):

        for rec in self:
            users = self.env['res.users'].browse(self._context.get('active_ids'))
            for user in users:
                user.password= self.new_b_passwd
            return {'type': 'ir.actions.client', 'tag': 'reload'}
