from odoo import models, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_pay_with_check(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Çek ile Ödeme',
            'res_model': 'account.check',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_amount': self.amount_residual,
                'default_partner_id': self.partner_id.id,
                'default_move_id': self.id,
            },
        }
