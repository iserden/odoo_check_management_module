from odoo import models, fields, api, _

class AccountCheckOnchange(models.Model):
    _inherit = 'account.check'

    # ONCHANGE METOTLARI (Alan Değişikliğine Tepki Verir)

    @api.onchange('journal_id')
    def _onchange_journal_id(self):
        """
        Muhasebe Defteri (Journal) alanı değiştiğinde, eğer seçilen defter bir banka hesabına bağlıysa,
        ilgili banka bilgilerini (banka, hesap numarası, IBAN) otomatik olarak doldurur.
        """
        if self.journal_id and self.journal_id.bank_account_id:
            bank_account = self.journal_id.bank_account_id
            self.bank_id = bank_account.bank_id.id
            self.account_number = bank_account.acc_number
            self.iban = bank_account.acc_number
            self.branch_code = False

        else:
            # Eğer bir muhasebe defteri seçilmezse veya banka hesabı yoksa ilgili alanları temizle
            self.bank_id = False
            self.account_number = False
            self.iban = False
            self.branch_code = False
