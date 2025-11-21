from odoo import models

class AccountCheck(models.Model):
    _inherit = 'account.check'

    def print_check_slip(self):
        report = self.env['ir.actions.report']._get_report_from_name('account_check_management.report_check_slip')
        return report.report_action(self)
