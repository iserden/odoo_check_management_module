from odoo import models, fields

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    check_number = fields.Char(string='Çek No')
    check_due_date = fields.Date(string='Çek Vade Tarihi')
    check_bank = fields.Char(string='Çek Bankası')
    check_amount = fields.Monetary(string='Çek Tutarı', currency_field='currency_id')
    currency_id = fields.Many2one('res.currency', string='Para Birimi')
