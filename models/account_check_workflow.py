from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountCheck(models.Model):
    _inherit = 'account.check'
    # İŞ AKIŞI (WORKFLOW) METOTLARI
   
    def action_to_portfolio(self):
        """
        Çekin durumunu 'Taslak'tan 'Portföyde'ye geçirir.
        """
        for check in self:
            if check.state != 'draft':
                raise ValidationError(_("Çek sadece 'Yeni' durumdayken portföye alınabilir."))
            check.state = 'portfolio'
            if check.check_type == 'received':
                # Alınan çekler için mevcut kayıt
                check._create_account_move('101000', '102001', check.amount, _('Çek portföye alındı'))
            elif check.check_type == 'issued':
                # Verilen çekler için: Verilen Çekler borç, Banka alacak
                check._create_account_move('103000', '102001', check.amount, _('Çek verildi'))

    def action_to_bank_collection(self):
        """
        Çekin durumunu 'Portföyde'den 'Bankaya Tahsile Verildi'ye geçirir.
        """
        for check in self:
            if check.state != 'portfolio':
                raise ValidationError(_("Çek portföyde olmadan bankaya tahsile verilemez."))
            check.state = 'bank_collection'
            # Otomatik muhasebe kaydı: Tasdik Edilmemiş Ödemeler (102998) borç, Alınan Çekler (101000) alacak
            check._create_account_move('102998', '101000', check.amount, _('Çek bankaya tahsile verildi'))

    def action_collected(self):
        """
        Çekin durumunu 'Portföyde' veya 'Bankaya Tahsile Verildi'den 'Tahsil Edildi'ye geçirir.
        """
        for check in self:
            if check.state not in ['portfolio', 'bank_collection']:
                raise ValidationError(_("Çek tahsilat için uygun durumda değil."))
            check.state = 'collected'
            if check.check_type == 'received':
                # Alınan çekler için mevcut kayıt
                check._create_account_move('102001', '102998', check.amount, _('Çek tahsil edildi'))
            elif check.check_type == 'issued':
                # Verilen çekler için: Banka borç, Verilen Çekler alacak
                check._create_account_move('102001', '103000', check.amount, _('Verilen çek tahsil edildi'))

    def action_bounced(self):
        """
        Çekin durumunu 'Portföyde' veya 'Bankaya Tahsile Verildi'den 'Karşılıksız'a geçirir.
        """
        for check in self:
            if check.state not in ['portfolio', 'bank_collection']:
                raise ValidationError(_("Çek karşılıksız olarak işaretlenmek için uygun durumda değil."))
            check.state = 'bounced'
            if check.check_type == 'received':
                # Alınan çekler için mevcut kayıt
                check._create_account_move('102997', '102998', check.amount, _('Çek karşılıksız çıktı'))
            elif check.check_type == 'issued':
                # Verilen çekler için: Tahsil Edilmeyen Ödemeler borç, Verilen Çekler alacak
                check._create_account_move('102997', '103000', check.amount, _('Verilen çek karşılıksız çıktı'))

    def _create_account_move(self, debit_code, credit_code, amount, narration):
        account_obj = self.env['account.account']
        debit_account = account_obj.search([('code', '=', debit_code)], limit=1)
        credit_account = account_obj.search([('code', '=', credit_code)], limit=1)
        if not debit_account or not credit_account:
            raise ValidationError(_(f"Muhasebe hesapları bulunamadı: {debit_code}, {credit_code}"))
        move_vals = {
            'date': fields.Date.today(),
            'ref': self.name or '',
            'journal_id': self.env['account.journal'].search([('type', '=', 'bank')], limit=1).id,
            'line_ids': [
                (0, 0, {
                    'account_id': debit_account.id,
                    'name': narration,
                    'debit': amount,
                    'credit': 0.0,
                }),
                (0, 0, {
                    'account_id': credit_account.id,
                    'name': narration,
                    'debit': 0.0,
                    'credit': amount,
                }),
            ],
            'narration': narration,
        }
        move = self.env['account.move'].create(move_vals)
        move.action_post()

    def action_draft(self):
        """
        Çekin durumunu taslağa geri çeker.
        """
        for check in self:
            if check.state == 'collected':
                raise ValidationError(_("Tahsil edilmiş bir çek taslağa geri alınamaz."))
            check.state = 'draft'

    def action_endorsed(self):
        """
        Çeki 'Ciro Edildi' durumuna geçirir ve ciro bilgisi girişi için form açar.
        """
        self.ensure_one()
        if self.check_type == 'issued':
            raise ValidationError(_('Verilen çeklerde ciro işlemi yapılamaz.'))
        self.state = 'endorsed'
        self.message_post(body="Çek ciro edildi.")
        # Otomatik muhasebe kaydı: Likidite Transferi (103001) borç, Alınan Çekler (101000) alacak
        self._create_account_move('103001', '101000', self.amount, _('Çek ciro edildi'))
        return {
            'type': 'ir.actions.act_window',
            'name': 'Ciro Bilgisi Gir',
            'res_model': 'circulated.check',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_account_check_id': self.id,
            }
        }