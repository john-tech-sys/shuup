# -*- coding: utf-8 -*-
# This file is part of Shuup.
#
# Copyright (c) 2012-2020, Shoop Commerce Ltd. All rights reserved.
#
# This source code is licensed under the OSL-3.0 license found in the
# LICENSE file in the root directory of this source tree.
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models.fields.related import ManyToManyField
from django.utils.translation import ugettext_lazy as _

from shuup.core.fields import CurrencyField, MoneyValueField, TaggedJSONField
from shuup.core.models import Contact, PersonContact, Product, Shop
from shuup.utils.properties import (
    MoneyPropped, TaxfulPriceProperty, TaxlessPriceProperty
)


def generate_key():
    return uuid4().hex


class StoredBasket(MoneyPropped, models.Model):
    # A combination of the PK and key is used to retrieve a basket for session situations.
    key = models.CharField(max_length=32, default=generate_key, verbose_name=_('key'))

    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, verbose_name=_('shop'))

    customer = models.ForeignKey(
        Contact, blank=True, null=True,
        on_delete=models.CASCADE,
        related_name="customer_baskets",
        verbose_name=_('customer')
    )
    orderer = models.ForeignKey(
        PersonContact, blank=True, null=True,
        on_delete=models.CASCADE,
        related_name="orderer_baskets",
        verbose_name=_('orderer')
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.CASCADE,
        related_name="baskets_created",
        verbose_name=_('creator')
    )

    created_on = models.DateTimeField(auto_now_add=True, db_index=True, editable=False, verbose_name=_('created on'))
    updated_on = models.DateTimeField(auto_now=True, db_index=True, editable=False, verbose_name=_('updated on'))
    persistent = models.BooleanField(db_index=True, default=False, verbose_name=_('persistent'))
    deleted = models.BooleanField(db_index=True, default=False, verbose_name=_('deleted'))
    finished = models.BooleanField(db_index=True, default=False, verbose_name=_('finished'))
    title = models.CharField(max_length=64, blank=True, verbose_name=_('title'))
    data = TaggedJSONField(verbose_name=_('data'))

    # For statistics etc., as `data` is opaque:
    taxful_total_price = TaxfulPriceProperty('taxful_total_price_value', 'currency')
    taxless_total_price = TaxlessPriceProperty('taxless_total_price_value', 'currency')

    taxless_total_price_value = MoneyValueField(default=0, null=True, blank=True, verbose_name=_('taxless total price'))
    taxful_total_price_value = MoneyValueField(default=0, null=True, blank=True, verbose_name=_('taxful total price'))
    currency = CurrencyField(verbose_name=_('currency'))
    prices_include_tax = models.BooleanField(verbose_name=_('prices include tax'))

    product_count = models.IntegerField(default=0, verbose_name=_('product_count'))
    products = ManyToManyField(Product, blank=True, verbose_name=_('products'))

    class Meta:
        app_label = "shuup_front"
        verbose_name = _('stored basket')
        verbose_name_plural = _('stored baskets')
