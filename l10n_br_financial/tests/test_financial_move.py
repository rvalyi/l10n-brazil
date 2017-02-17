# -*- coding: utf-8 -*-
# Copyright 2017 KMEE
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
import time


class TestFinancialMove(TransactionCase):

    def setUp(self):
        super(TestFinancialMove, self).setUp()
        self.main_company = self.env.ref('base.main_company')
        self.currency_euro = self.env.ref('base.EUR')
        self.financial_move = self.env['financial.move']
        self.partner_agrolait = self.env.ref("base.res_partner_2")
        self.partner_axelor = self.env.ref("base.res_partner_2")

    def create_receivable_100(self):
        cr_4 = self.financial_move.create(
            dict(
                move_type='r',
                company_id=self.main_company.id,
                currency_id=self.currency_euro.id,
                amount_document=100.00,
                partner_id=self.partner_agrolait.id,
            )
        )
        return cr_4

    """ US1 # Como um operador de cobrança, eu gostaria de cadastrar uma conta
     a receber/pagar para manter controle sobre o fluxo de caixa.
    """
    def test_us_1_ac_1(self):
        """ DADO a data de vencimento de 27/02/2017
        QUANDO criado um lançamento de contas a receber
        ENTÃO a data de vencimento útil deve ser de 01/03/2017"""
        cr_1 = self.financial_move.create(dict(
            due_date='2017-02-27',
            company_id=self.main_company.id,
            currency_id=self.currency_euro.id,
            amount_document=100.00,
            partner_id=self.partner_agrolait.id,
            document_date=time.strftime('%Y') + '-01-01',
            document_number='1111',
            move_type='r',
        ))
        self.assertEqual(cr_1.business_due_date, '2017-03-01')

    def test_us_1_ac_2(self):
        """DADO uma conta a pagar ou receber
        QUANDO o valor for igual a zero
        ENTÃO apresentar uma mensagem solicitando preenchimento de valor
            maior que zero
        E impedir lançamento"""
        with self.assertRaises(ValidationError):
            self.financial_move.create(dict(
                due_date='2017-02-27',
                company_id=self.main_company.id,
                currency_id=self.currency_euro.id,
                amount_document=0.00,
                partner_id=self.partner_agrolait.id,
                document_date=time.strftime('%Y') + '-01-02',
                document_number='2222',
                move_type='r',
            ))

            self.financial_move.create(dict(
                due_date='2017-02-27',
                company_id=self.main_company.id,
                currency_id=self.currency_euro.id,
                amount_document=-10.00,
                partner_id=self.partner_agrolait.id,
                document_date=time.strftime('%Y') + '-01-03',
                document_number='3333',
                move_type='r',
            ))

    def test_us1_ac_3(self):
        """ DADO a criação de uma nova parcela
        QUANDO confirmada
        ENTÃO esta parcela deve ter um número sequencial único chamado
         de código da parcela
        :return:
        """
        cr_1 = self.financial_move.create(dict(
            due_date=time.strftime('%Y') + '-01-10',
            company_id=self.main_company.id,
            currency_id=self.currency_euro.id,
            amount_document=100.00,
            partner_id=self.partner_agrolait.id,
            document_date=time.strftime('%Y') + '-01-04',
            document_number='4444',
            move_type='r',
        ))

    def test_us1_ac_4(self):
        """ DADO a criação de uma nova parcela
        QUANDO confirmada
        ENTÃO os seus campos não poderão mais ser alterados pela
        interface de cadastro
        :return:
        """
        pass

    """ Como um operador de cobrança, eu gostaria de alterar o vencimento ou
    valor de uma conta a receber/pagar para auditar as alterações do fluxo
    de caixa."""

    def test_us2_ac_1(self):
        """ DADO a alteração de uma parcela via assistente
        QUANDO solicitada a alteração do vencimento
        OU valor
        ENTÃO deve ser registrado o histórico no
            histórico da alteração o motivo
        E a alteração dos campos

        :return:
        """
        pass

    def test_3(self):
        """DADO que existe uma parcela de 100 reais em aberto
        QUANDO for recebido/pago 100 reais
        ENTÃO o valor do balanço da parcela deve ser 0
        E o status da parcela deve mudar para pago."""
        cr_4 = self.create_receivable_100()
        cr_4.action_confirm()
        pay = self.financial_move.create(
            dict(
                move_type='rr',
                company_id=self.main_company.id,
                currency_id=self.currency_euro.id,
                amount_document=100.00,
                payment_id=cr_4.id
            )
        )
        pay.action_confirm()
        self.assertEqual(0.00, cr_4.balance)
        self.assertEqual('paid', cr_4.state)
