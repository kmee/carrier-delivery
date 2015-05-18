# -*- coding: utf-8 -*-
# #############################################################################
#
#    Brazillian Carrier Correios Sigep WEB
#    Copyright (C) 2015 KMEE (http://www.kmee.com.br)
#    @author Luis Felipe Mileo <mileo@kmee.com.br>
#    @author: Michell Stuttgart <michell.stuttgartx@kmee.com.br>
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
# from openerp import orm
#
# class ResPartner(orm.Model):
#
#     def search_cep(self, cr, uid, ids , cep):


from pysigep_web.pysigepweb.webservice_atende_cliente import \
    WebserviceAtendeCliente
from pysigep_web.pysigepweb.webservice_calcula_preco_prazo import \
    WebserviceCalculaPrecoPrazo
from pysigep_web.pysigepweb.webservice_rastreamento import WebserviceRastreamento
from pysigep_web.pysigepweb.tag_nacional import TagNacionalPAC41068
from pysigep_web.pysigepweb.usuario import Usuario
from pysigep_web.pysigepweb.tag_plp import TagPLP
from pysigep_web.pysigepweb.tag_remetente import TagRemetente
from pysigep_web.pysigepweb.tag_dimensao_objeto import *
from pysigep_web.pysigepweb.tag_objeto_postal import *
from pysigep_web.pysigepweb.tag_correios_log import TagCorreiosLog
from pysigep_web.pysigepweb.diretoria import Diretoria
from pysigep_web.pysigepweb.endereco import Endereco


def main():

    usr = Usuario('sigep', 'n5f9t8', '34028316000103', '08082650',
                  '9912208555', '0057018901')

    # l = [ServicoPostagem(ServicoPostagem.SERVICO_CARTA_COMERCIAL_A_FATURAR),
    #      ServicoPostagem(ServicoPostagem.SERVICO_PAC_41068)]

    # try:
    print u'[INFO] Iniciando ServiÃ§o de Atendimento ao  Cliente'
    sv = WebserviceAtendeCliente(
        WebserviceAtendeCliente.AMBIENTE_HOMOLOGACAO, usr)
    # except ErroServidorNaoEncontrado as e:
    #     print e.message

    print
    print 'Cosultando dados do cliente'
    busca_cliente = sv.busca_cliente()

    print
    print u'[INFO] Verificando disponibilidade dos serviÃ§os:'
    print '[INFO] Resultado da consulta para os cep %s (origem) e %s (' \
          'destino):' % ('70002-900', '74000100')
    print '[INFO] Status da consulta:'
    lista_servicos = \
        busca_cliente.contratos[0].cartoes_postagem[0].servicos_postagem
    res = sv.verifica_disponibilidade_servicos(lista_servicos,
                                               '70002900',
                                               '74000100')

    for serv, status in res.items():
        print serv, ' ', status

    print
    print '[INFO] Consulta cep: %s' % '70002900'
    end_erp = sv.consulta_cep('70002900')
    print 'Bairro: ', end_erp.bairro
    print 'CEP:', end_erp.cep
    print 'Cidade: ', end_erp.cidade
    print 'Complemento: ', end_erp.complemento
    print u'EndereÃ§o: ', end_erp.end
    print 'Id:', end_erp.id
    print 'UF:', end_erp.uf

    print
    print u'[INFO] Verificando status do cartÃ£o de postagem'
    print sv.consulta_status_cartao_postagem(usr.num_cartao_postagem)

    print
    # sv_postagem = ServicoPostagem(ServicoPostagem.SERVICO_PAC_41068)
    sv_postagem = busca_cliente.contratos[0].cartoes_postagem[
        0].servicos_postagem[0]

    qtd_etiquetas = 3
    print '[INFO] Solicitando %d etiquetas...' % qtd_etiquetas
    etiquetas = sv.solicita_etiquetas(sv_postagem.servico_postagem_id,
                                      qtd_etiquetas=qtd_etiquetas)

    for i in range(len(etiquetas)):
        print etiquetas[i].valor

    print
    print '[INFO] Solicitando digito verificador para etiquetas...'
    print sv.gera_digito_verificador_etiquetas(
        etiquetas, online=False)

    remetente_endereco = Endereco(logradouro='Avenida Central', numero=2370,
                                  bairro='Centro', cep=70002900,
                                  cidade=u'BrasÃ­lia', uf=Endereco.UF_PARANA,
                                  complemento=u'sala 1205,12Â° andar')

    destinatario_endereco = Endereco(logradouro='Avenida Central',
                                     numero=1065, bairro='Setor Industrial',
                                     cidade=u'GoiÃ¢nia', uf=Endereco.UF_GOIAS,
                                     cep=74000100, complemento='Qd:102 A Lt:04')

    # Montando xml do plp
    print
    print '[INFO] Montando xml'
    obj_tag_plp = TagPLP(usr.num_cartao_postagem)
    obj_remetente = TagRemetente(usr.nome, usr.num_contrato, usr.codigo_admin,
                                 remetente_endereco,
                                 Diretoria(Diretoria.DIRETORIA_DR_PARANA),
                                 telefone=6112345008, email='cli@mail.com.br')

    obj_destinatario = TagDestinatario('Destino Ltda', destinatario_endereco,
                                       telefone=6212349644)

    obj_nacional = TagNacionalPAC41068(destinatario_endereco, 102030, '1')

    obj_nacional.valor_a_cobrar = 23.01

    obj_servico_adicional = TagServicoAdicional()

    obj_servico_adicional.add_tipo_servico_adicional(
        TagServicoAdicional.TIPO_AVISO_RECEBIMENTO)

    obj_servico_adicional.add_tipo_servico_adicional(
        TagServicoAdicional.TIPO_VALOR_DECLARADO, 99.00)

    # Caixa(20, 30, 38)
    obj_dimensao_objeto = TagDimensaoObjeto(Caixa(18, 11, 20))

    obj_postal = TagObjetoPostal(obj_destinatario=obj_destinatario,
                                 obj_nacional=obj_nacional,
                                 obj_dimensao_objeto=obj_dimensao_objeto,
                                 obj_servico_adicional=obj_servico_adicional,
                                 obj_servico_postagem=sv_postagem,
                                 ob_etiqueta=etiquetas[0],
                                 peso=60, status_processamento=0)

    obj_correios_log = TagCorreiosLog('2.3', obj_tag_plp, obj_remetente,
                                      [obj_postal])

    print
    print u'[INFO] Fechando prÃ©-lista de postagem para varios serviÃ§os'
    print
    plp = sv.fecha_plp_varios_servicos(obj_correios_log, long(123), etiquetas)
    print
    print u'[INFO] PrÃ©-lista de postagem fechada'
    print u'[INFO] Novo PLP id: ', plp.id_plp_cliente
    print '[INFO] Salvando XML em disco'
    plp.salvar_xml('xml_plp/')
    print

    print '[INFO] Conectanco com webservice de calculo de prazo e preco'
    calc_preco_prazo = WebserviceCalculaPrecoPrazo(usr)

    retorno = calc_preco_prazo.calcula_preco_prazo([sv_postagem], '70002900',
                                                   '74000100', obj_postal.peso,
                                                   obj_dimensao_objeto, True,
                                                   99.00, True)

    print '[INFO] Retorno do metodo calculo de prazo e preco'
    for ret in retorno:
        print 'Codigo: ', ret.codigo
        print 'Valor: ', ret.valor
        print 'PrazoEntrega: ', ret.prazo_entrega
        print 'ValorMaoPropria: ', ret.valor_mao_propria
        print 'ValorAvisoRecebimento:', ret.valor_aviso_recebimento
        print 'ValorValorDeclarado: ', ret.valor_declarado
        print 'EntregaDomiciliar: ', ret.entrega_domiciliar
        print 'EntregaSabado: ', ret.entrega_sabado
        print 'Erro: ', ret.erro
        print 'MsgErro: ', ret.msg_erro
        print 'ValorSemAdicionais: ', ret.valor_sem_adicionais
        print 'obsFim: ', ret.obs_fim
        print

    print
    print '[INFO] Rastreamento das etiquetas: ' + \
          'SS123456789BR; DM524874789BR; DM149692327BR; DG799572796BR'

    etqs = [Etiqueta('SS123456789BR'),
            Etiqueta('DM524874789BR'),
            Etiqueta('DM149692327BR'),
            Etiqueta('DG799572796BR')]

    usr.nome = 'ECT'
    usr.senha = 'SRO'
    rastreamento = WebserviceRastreamento(usr)
    rastreamento.path = '/tmp/'

    resp_rastr = rastreamento.rastrea_objetos(
        WebserviceRastreamento.TIPO_LISTA_ETIQUETAS,
        WebserviceRastreamento.RETORNAR_ULTIMO_EVENTO, etqs)

    print
    print 'Detalhes da etiqueta: ', resp_rastr.objetos['SS123456789BR'].numero
    print

    for evento in resp_rastr.objetos['SS123456789BR'].eventos:
        print 'Tipo evento: ', evento.tipo
        print 'Status evento: ', evento.status
        print 'Data evento: ', evento.data
        print 'Hora evento: ', evento.hora
        print 'Descricao evento: ', evento.descricao
        print 'Recebedor evento: ', evento.recebedor
        print 'Documento evento: ', evento.documento
        print 'comentario evento: ', evento.comentario
        print 'Local evento: ', evento.local
        print 'Codigo evento: ', evento.codigo
        print 'Cidade evento: ', evento.cidade
        print 'UF evento: ', evento.uf
        print 'STO: ', evento.sto

if __name__ == '__main__':
    main()
