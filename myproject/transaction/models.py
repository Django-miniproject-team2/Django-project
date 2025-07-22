
from django.conf import settings
from django.db import models
from django.utils import timezone  

class Transaction(models.Model):
    account = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='transactions',
        verbose_name="거래 계정"
    )

    amount = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="거래금액"
    )
    after = models.DecimalField(
        max_digits=15, decimal_places=2, help_text="거래 후 잔액"
    )
    account_details = models.CharField(
        max_length=255, help_text="예: 오픈뱅킹 출금, ATM 현금 입금, 올리브영 등"
    )

    TRANSACTION_TYPE_CHOICES = [
        ('cash', '현금'),
        ('transfer', '계좌 이체'),
        ('auto_transfer', '자동 이체'),
        ('card_payment', '카드 결제'),
    ]
    transaction_type = models.CharField(
        max_length=50,
        choices=TRANSACTION_TYPE_CHOICES,
        help_text="거래 유형"
    )

    DEPOSIT_WITHDRAWAL_CHOICES = [
        ('deposit', '입금'),
        ('withdrawal', '출금'),
    ]
    deposit_withdrawal_type = models.CharField(
        max_length=10,
        choices=DEPOSIT_WITHDRAWAL_CHOICES,
        help_text="입출금 여부"
    )

    transaction_date = models.DateTimeField(
        verbose_name="거래 일시",
        default=timezone.now  
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.transaction_date.strftime('%Y-%m-%d %H:%M')}] {self.account.email} - {self.amount}원 ({self.get_deposit_withdrawal_type_display()})"

    class Meta:
        verbose_name = "거래"
        verbose_name_plural = "거래 내역"
        ordering = ['-transaction_date']
