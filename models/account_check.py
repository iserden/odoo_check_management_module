from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AccountCheck(models.Model):
    _name = 'account.check'
    _description = 'Çek Yönetimi'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    # TEMEL ÇEK BİLGİLERİ
    name = fields.Char(
        string='Çek No',
        required=True,
        copy=False,
        default='Yeni',
        readonly=True,
        tracking=True,
        help="Çekin benzersiz numarası. Otomatik olarak oluşturulur."
    )
    check_type = fields.Selection([
        ('received', 'Alınan Çek'),
        ('issued', 'Verilen Çek'),
    ], string='Çek Tipi', required=True, tracking=True)
    amount = fields.Monetary(
        string='Tutar',
        required=True,
        currency_field='currency_id',
        tracking=True
    )
    currency_id = fields.Many2one(
        'res.currency',
        string='Para Birimi',
        default=lambda self: self.env.company.currency_id.id,
        required=True
    )
    due_date = fields.Date(
        string='Vade Tarihi',
        required=True,
        tracking=True,
        help="Çekin tahsil edilebileceği veya ödeneceği tarih."
    )
    issue_date = fields.Date(
        string='Keşide Tarihi',
        required=True,
        default=fields.Date.context_today,
        help="Çekin düzenlendiği tarih."
    )
    issue_place = fields.Char(
        string='Keşide Yeri',
        help="Çekin düzenlendiği şehir veya yer."
    )

    # ÇEK İLE İLİŞKİLİ TARAFLAR
    partner_id = fields.Many2one(
        'res.partner',
        string='İlişkili Cari Hesap',
        required=True,
        help="Bu çekin ilişkili olduğu ana müşteri veya tedarikçi."
    )
    drawer_partner_id = fields.Many2one(
        'res.partner',
        string='Keşideci',
        help="Çeki düzenleyen kişi veya kurum."
    )
    payee_partner_id = fields.Many2one(
        'res.partner',
        string='Lehtar',
        help="Çeki tahsil edecek kişi veya kurum."
    )

    # BANKA VE HESAP BİLGİLERİ
    bank_id = fields.Many2one(
        'res.bank',
        string='Banka',
        help="Çekin ait olduğu banka."
    )
    branch_code = fields.Char(
        string='Şube Kodu',
        help="Banka şubesinin kodu."
    )
    account_number = fields.Char(
        string='Hesap Numarası',
        help="Çekin ilişkili olduğu hesap numarası."
    )
    iban = fields.Char(
        string='IBAN',
        help="Uluslararası Banka Hesap Numarası."
    )
    portfolio_number = fields.Char(
        string='Portföy No',
        copy=False,
        help="Çekin portföyde aldığı numara."
    )
    serial_number = fields.Char(
        string='Seri No',
        copy=False,
        help="Çekin seri numarası."
    )

    # DURUM VE İŞ AKIŞI YÖNETİMİ
    state = fields.Selection([
        ('draft', 'Yeni'),
        ('portfolio', 'Portföyde'),
        ('bank_collection', 'Bankaya Tahsile Verildi'),
        ('collected', 'Tahsil Edildi'),
        ('bounced', 'Karşılıksız'),
        ('endorsed', 'Ciro Edildi'),
        ('returned', 'Geri Alındı / İade Edildi'),
    ], string='Durum', default='draft', tracking=True, help="Çekin mevcut durumu.")

    # MUHASEBE ENTEGRASYONU
    journal_id = fields.Many2one(
        'account.journal',
        string='Muhasebe Defteri',
        domain="[('type', 'in', ('bank', 'cash'))]",
        help="Çek hareketinin kaydedileceği muhasebe defteri."
    )
    move_id = fields.Many2one(
        'account.move',
        string='Muhasebe Fişi',
        readonly=True,
        copy=False,
        help="Bu çekle ilişkili otomatik oluşturulan muhasebe fişi."
    )

    # EK BİLGİLER
    note = fields.Text(string='Not', help="Çekle ilgili ek notlar veya açıklamalar.")

    circulated_check_ids = fields.One2many(
        'circulated.check',
        'account_check_id',
        string='Ciro Bilgileri'
    )

    # OLUŞTURMA METODU
    @api.model
    def create(self, vals):
        """
        Yeni bir çek kaydı oluşturulduğunda otomatik numara atar.
        """
        if vals.get('name', 'Yeni') == 'Yeni':
            vals['name'] = self.env['ir.sequence'].next_by_code('account.check.sequence') or _('Yeni')
        return super(AccountCheck, self).create(vals)
