# -*- coding: utf-8 -*-
# #############################################################################
#
#    Brazillian Carrier Correios Sigep WEB
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Mileo <mileo@kmee.com.br>
#    @author: Michell Stuttgart <michell.stuttgart@kmee.com.br>
#
#    Sponsored by Europestar www.europestar.com.br
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


#
# from . import res_config, contract, directorship, post_card, post_service, \
#     delivery, stock, sale, shipping_response, company

from . import shipping_response
from . import contract
from . import directorship
from . import post_card
from . import post_service
from . import delivery
from . import stock
from . import sale
from . import company
from . import res_config

#TODO: Adicionar opcao de selecionar os servicos adicionais na Ordem de Entrega
#TODO: Adicionar field partner_id em res_company para guardamos o partner correio
#TODO: Adicionar numero e serie da fatura na PLP quando a encomenda for do tipo PAC
#TODO: Inserir campos de dimensao do objeto em cada Ordem de Entrega (PLP e
# etiqueta)
#TODO: Verificar tamanho das caixas usadas
#TODO: Montar workflow da PLP
#TODO: Montar ficha de postagem dos correios com chancela, qrcode e cod. barras
#TODO: Adicionar campos na ficha de dados da PLP
#TODO: Verificar se PLP não pode mais ser usada depois de gerada.as
#TODO: Pesquisar o que é id_plp_master
#TODO: Adicionar Warning para erro de validação do xml da PLP