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

from . import shipping_response
from . import contract
from . import directorship
from . import post_card
from . import post_service
from . import delivery
from . import stock
from . import company
from . import res_config

#TODO: Montar ficha de postagem dos correios com chancela, qrcode e cod. barras
#TODO: Adicionar campos no relatorio do vouncher da PLP
#TODO: O botão atualizar do Pedido de Venda pode ser usado para atualizar o
# frete
#TODO: Remover o botão "adicionar ao orçamento". O "Atualizar" já serviria
# pra isso. Só no momento de salvar que o recalculo poderia ser automatico
# funcionando da mesma maneira que o "Atualizar"
#TODO: Anexar xml da PLP da view da PLP
#TODO: Inserir campos de dimensao do objeto em cada Ordem de Entrega (PLP e
# etiqueta)
#TODO: Adicionar opcao de selecionar os servicos adicionais na Ordem de Entrega
#TODO: Verificar se PLP não pode mais ser usada depois de gerada
#TODO: Pesquisar o que é id_plp_master
#TODO: Verificar tamanho das caixas usadas
#TODO: Unidade usada para peso: kilos
#TODO: Unidade usada para volume: m3
#TODO: Unidade usada para comprimento: m
#TODO: O peso presente na ordem de entrega corresponde ao peso de uma unidade
#  ou se trata do peso total de todos os volumes
