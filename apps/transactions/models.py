from django.db import models

from apps.accounts.models import Account

# 거래 종류
TRANSACTION_TYPE_CHOICES = [
    ("ATM", "ATM 거래"),
    ("TRANSFER", "계좌이체"),
    ("AUTOMATIC_TRANSFER", "자동이체"),
    ("CARD", "카드결제"),
    ("INTEREST", "이자"),
]
# 거래 타입
DEPOSIT_WITHDRAWAL_CHOICES = [
    ("DEPOSIT", "입금"),
    ("WITHDRAW", "출금"),
]


class Transaction(models.Model):
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="계좌 정보",
    )
    amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="거래 금액"
    )
    balance_after = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="거래 후 잔액"
    )
    description = models.CharField(max_length=255, blank=True, help_text="거래 내역")

    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE_CHOICES, help_text="거래 타입"
    )

    io_type = models.CharField(
        max_length=10, choices=DEPOSIT_WITHDRAWAL_CHOICES, help_text="입출금 타입"
    )

    transaction_date = models.DateTimeField(
        verbose_name="거래 일시",
        auto_now_add=True,
    )
    transaction_updated = models.DateTimeField(
        auto_now=True,
        verbose_name="거래 내역 수정 일시",
    )

    def __str__(self):
        return f"[{self.account.account_number}] {self.get_io_type_display()} {self.amount} - {self.description}"

    class Meta:
        verbose_name = "거래 내역"
        verbose_name_plural = "거래 내역들"
