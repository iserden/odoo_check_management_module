from odoo import models, fields

class CirculatedCheck(models.Model):
    _name = 'circulated.check'
    _description = 'Ciro Edilen Çek Bilgisi'

    account_check_id = fields.Many2one(
        'account.check',
        string='İlgili Çek',
        required=True,
        ondelete='cascade',
    )
    company_name = fields.Char(
        string='Şirket Adı',
        required=True
    )
    tax_number = fields.Char(string='Vergi Numarası')
    address = fields.Text(string='Adres')
    circulation_date = fields.Date(
        string='Ciro Tarihi',
        default=fields.Date.today,
    )
    notes = fields.Text(string='Notlar')