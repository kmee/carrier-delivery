## -*- coding: utf-8 -*-

<html>
<head>
<style type="text/css">
    ${css}

.list_main_table {
    border: thin solid #E3E4EA;
    text-align: center;
    border-collapse: collapse;
}

table.list_main_table {
    margin-top: 20px;
}

.list_main_headers {
    padding: 0;
}

.list_main_headers th {
    border: thin solid #000000;
    padding-right: 3px;
    padding-left: 3px;
    background-color: #EEEEEE;
    text-align: center;
    font-size: 12;
    font-weight: bold;
}

.list_main_table td {
    padding-right: 3px;
    padding-left: 3px;
    padding-top: 3px;
    padding-bottom: 3px;
}

.list_main_lines,
.list_main_footers {
    padding: 0;
}

.list_main_footers {
    padding-top: 15px;
}

.list_main_lines td,
.list_main_footers td,
.list_main_footers th {
    text-align: left;
    font-size: 12;
}

.list_main_lines td {
    border-bottom: thin solid #EEEEEE
}

.list_main_footers td {
    border: thin solid #ffffff;
}

.list_main_footers th {
    text-align: right;
}

td .total_empty_cell {
    width: 77%;
}

td .total_sum_cell {
    width: 13%;
}

tfoot.totals tr:first-child td {
    padding-top: 15px;
}

.nobreak {
    page-break-inside: avoid;
}

caption.formatted_note {
    text-align: left;
    border-right: thin solid #EEEEEE;
    border-left: thin solid #EEEEEE;
    border-top: thin solid #EEEEEE;
    padding-left: 10px;
    font-size: 11;
    caption-side: bottom;
}

caption.formatted_note p {
    margin: 0;
}

.list_bank_table {
    text-align: center;
    border-collapse: collapse;
    page-break-inside: avoid;
    display: table;
}

.act_as_row {
    display: table-row;
}

.list_bank_table .act_as_thead {
    background-color: #EEEEEE;
    text-align: left;
    font-size: 12;
    font-weight: bold;
    padding-right: 3px;
    padding-left: 3px;
    white-space: nowrap;
    background-clip: border-box;
    display: table-cell;
}

.list_bank_table .act_as_cell {
    text-align: left;
    font-size: 12;
    padding-right: 3px;
    padding-left: 3px;
    padding-top: 3px;
    padding-bottom: 3px;
    white-space: nowrap;
    display: table-cell;
}

.list_tax_table {
}

.list_tax_table td {
    text-align: left;
    font-size: 12;
}

.list_tax_table th {
}

.list_tax_table thead {
    display: table-header-group;
}

.list_total_table {
    border: thin solid #E3E4EA;
    text-align: center;
    border-collapse: collapse;
}

.list_total_table td {
    border-top: thin solid #EEEEEE;
    text-align: left;
    font-size: 12;
    padding-right: 3px;
    padding-left: 3px;
    padding-top: 3px;
    padding-bottom: 3px;
}

.list_total_table th {
    background-color: #EEEEEE;
    border: thin solid #000000;
    text-align: center;
    font-size: 12;
    font-weight: bold;
    padding-right: 3px padding-left : 3 px
}

.list_total_table thead {
    display: table-header-group;
}

.right_table {
    right: 4cm;
    width: "100%";
}

.std_text {
    font-size: 12;
}

td.amount, th.amount {
    text-align: right;
    white-space: nowrap;
}

td.date {
    white-space: nowrap;
    width: 90px;
}

td.vat {
    white-space: nowrap;
}

.address .recipient {
    font-size: 12px;
    margin-left: 350px;
    margin-right: 120px;
    float: right;
}

.main_col1 {
    width: 40%;
}

td.main_col1 {
    text-align: left;
    vertical-align: top;
}

.main_col2 {
    width: 10%;
    vertical-align: top;
}

.main_col3 {
    width: 10%;
    text-align: center;
    vertical-align: top;
}

.main_col6 {
    width: 10%;
    vertical-align: top;
}

.main_col4 {
    width: 10%;
    text-align: right;
    vertical-align: top;
}

.main_col5 {
    width: 7%;
    text-align: left;
    vertical-align: top;
}

.main_col7 {
    width: 13%;
    vertical-align: top;
}

</style>

</head>
<body>
    %for plp in objects:

        <% services = get_post_services(user.id, plp.id) %>
        <table border="0" cellpadding="1" cellspacing="1" style="width: 100%;">
            <tbody>
            <tr>
                <td style="width: 20%;"><img
                        src="data:image/png;base64,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"
                        style="height: 29px; width: 120px;"/></td>
                <td style="text-align: center; vertical-align: bottom;"><span
                        style="font-size:16px;"><strong>EMPRESA BRASILEIRA DE
                    CORREIOS E TEL&Eacute;GRAFOS</strong></span></td>
            </tr>
            </tbody>
        </table>

        <table border="1" cellspacing="0"
               style="border: 1px solid black; width: 100%;">
            <tbody>
            <tr>
                <td style="text-align: center;"><span
                        style="font-size:16px;"><strong>PR&Eacute; LISTA DE
                    POSTAGEM
                    - PLP - SIGEP WEB</strong></span></td>
            </tr>
            <tr>
                <td>
                    <table border="0" cellpadding="1" cellspacing="0"
                           style="white-space: nowrap; width: 100%;">
                        <tbody>
                        <tr>
                            <td>
                                <table border="0" cellpadding="1"
                                       cellspacing="0"
                                       style="width: 100%;">
                                    <tbody>
                                    <tr>
                                        <td style="width: 45%;"><strong>SIGEP
                                            WEB -
                                            Gerenciador de postagem dos
                                            correios</strong></td>
                                    </tr>
                                    <tr>
                                        <td style="width: 45%;"><strong>Contrado:
                                            &nbsp;
                                        </strong>${plp.contract_id.number}
                                        </td>
                                    </tr>

                                    <tr>
                                        <td style="width: 45%;"><strong>Cliente:
                                            &nbsp;
                                        </strong>${plp.company_id.name}</td>
                                    </tr>
                                    <tr>
                                        <td style="width: 45%;"><strong>Telefone
                                            de
                                            contato: </strong>${plp.company_id.phone}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="width: 45%;"><strong>Email de
                                            contato: </strong>${plp.company_id.email}
                                        </td>
                                    </tr>
                                    </tbody>
                                </table>
                            </td>
                            <td style="text-align: center; vertical-align: middle;">
                                <table border="0" cellpadding="1"
                                       cellspacing="1"
                                       style="width: 100%;">
                                    <tbody>
                                    <tr>
                                        <td><strong>N&deg;
                                            PLP: ${plp.carrier_tracking_ref}</strong>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><span
                                                style="text-align: center; white-space: nowrap;">
                                            %if plp.barcode_id:
                                                <img src='data:image/png;base64,${plp.barcode_id.image}'/>
                                            %else:
                                                ' '
                                            %endif
                                        </span>
                                        </td>
                                    </tr>
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td>
                    <table border="0" cellpadding="1" cellspacing="1"
                           style="width: 100%;">
                        <tbody>
                        <tr>
                            <td style="vertical-align: top;">
                                <table border="0" cellpadding="1"
                                       cellspacing="1"
                                       style="width: 100%;">
                                    <tbody>
                                    <tr>
                                        <td style="width: 33%;"><strong>C&oacute;d.
                                            Servi&ccedil;o:</strong></td>
                                        <td style="width: 33%;">
                                            <strong>Quantidade:</strong></td>
                                        <td style="width: 33%;"><strong>Servi&ccedil;o:</strong>
                                        </td>
                                    </tr>
                                        <% total = 0 %>
                                        % for key, value in services.items():
                                            <tr>
                                                <td>${value['code']}</td>
                                                <td>${value['quant']}</td>
                                                <td>${value['name']}</td>
                                            </tr>
                                            <% total += value['quant'] %>
                                        % endfor
                                    <tr>
                                        <td><strong>Total:</strong></td>
                                        <td>${total}</td>
                                        <td>&nbsp;</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </td>
                            <td style="width: 25%;">
                                <p><strong>Data da entrega:</strong>
                                    %if plp.date:
                                        ${plp.date}
                                    %else:
                                        ''
                                    %endif
                                </p>

                                <p>&nbsp;</p>

                                <p style="text-decoration: overline;">
                                    Assinatura/Matr&iacute;cula dos Correios</p>

                                <p>1&ordf; via - Correios</p>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </td>
            </tr>

        </table>
        </tbody>
        </table>
        <hr size="1" style="border:1px dashed;">
        <table border="0" cellpadding="1" cellspacing="1" style="width: 100%;">
            <tbody>
            <tr>
                <td style="width: 20%;"><img
                        src="data:image/png;base64,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"
                        style="height: 29px; width: 120px;"/></td>
                <td style="text-align: center; vertical-align: bottom;"><span
                        style="font-size:16px;"><strong>EMPRESA BRASILEIRA DE
                    CORREIOS E TEL&Eacute;GRAFOS</strong></span></td>
            </tr>
            </tbody>
        </table>

        <table border="1" cellspacing="0"
               style="border: 1px solid black; width: 100%;">
            <tbody>
            <tr>
                <td style="text-align: center;"><span
                        style="font-size:16px;"><strong>PR&Eacute; LISTA DE
                    POSTAGEM
                    - PLP - SIGEP WEB</strong></span></td>
            </tr>
            <tr>
                <td>
                    <table border="0" cellpadding="1" cellspacing="0"
                           style="white-space: nowrap; width: 100%;">
                        <tbody>
                        <tr>
                            <td>
                                <table border="0" cellpadding="1"
                                       cellspacing="0"
                                       style="width: 100%;">
                                    <tbody>
                                    <tr>
                                        <td style="width: 45%;"><strong>SIGEP
                                            WEB -
                                            Gerenciador de postagem dos
                                            correios</strong></td>
                                    </tr>
                                    <tr>
                                        <td style="width: 45%;"><strong>Contrado:
                                            &nbsp;
                                        </strong>${plp.contract_id.number}
                                        </td>
                                    </tr>

                                    <tr>
                                        <td style="width: 45%;"><strong>Cliente:
                                            &nbsp;
                                        </strong>${plp.company_id.name}</td>
                                    </tr>
                                    <tr>
                                        <td style="width: 45%;"><strong>Telefone
                                            de
                                            contato: </strong>${plp.company_id.phone}
                                        </td>
                                    </tr>
                                    <tr>
                                        <td style="width: 45%;"><strong>Email de
                                            contato: </strong>${plp.company_id.email}
                                        </td>
                                    </tr>
                                    </tbody>
                                </table>
                            </td>
                            <td style="text-align: center; vertical-align: middle;">
                                <table border="0" cellpadding="1"
                                       cellspacing="1"
                                       style="width: 100%;">
                                    <tbody>
                                    <tr>
                                        <td><strong>N&deg;
                                            PLP: ${plp.carrier_tracking_ref}</strong>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><span
                                                style="text-align: center; white-space: nowrap;">
                                            %if plp.barcode_id:
                                                <img src='data:image/png;base64,${plp.barcode_id.image}'/>
                                            %else:
                                                ' '
                                            %endif
                                        </span>
                                        </td>
                                    </tr>
                                    </tbody>
                                </table>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
            <tr>
                <td>
                    <table border="0" cellpadding="1" cellspacing="1"
                           style="width: 100%;">
                        <tbody>
                        <tr>
                            <td style="vertical-align: top;">
                                <table border="0" cellpadding="1"
                                       cellspacing="1"
                                       style="width: 100%;">
                                    <tbody>
                                    <tr>
                                        <td style="width: 33%;"><strong>C&oacute;d.
                                            Servi&ccedil;o:</strong></td>
                                        <td style="width: 33%;">
                                            <strong>Quantidade:</strong></td>
                                        <td style="width: 33%;"><strong>Servi&ccedil;o:</strong>
                                        </td>
                                    </tr>
                                        <% total = 0 %>
                                        % for key, value in services.items():
                                            <tr>
                                                <td>${value['code']}</td>
                                                <td>${value['quant']}</td>
                                                <td>${value['name']}</td>
                                            </tr>
                                            <% total += value['quant'] %>
                                        % endfor
                                    <tr>
                                        <td><strong>Total:</strong></td>
                                        <td>${total}</td>
                                        <td>&nbsp;</td>
                                    </tr>
                                    </tbody>
                                </table>
                            </td>
                            <td style="width: 25%;">
                                <p><strong>Data da entrega:</strong>
                                    %if plp.date:
                                        ${plp.date}
                                    %else:
                                        ''
                                    %endif
                                </p>

                                <p>&nbsp;</p>

                                <p style="text-decoration: overline;">
                                    Assinatura/Matr&iacute;cula dos Correios</p>

                                <p>2&ordf; via - Correios</p>
                            </td>
                        </tr>
                        </tbody>
                    </table>
                </td>
            </tr>
        </table>
        </tbody>
        </table>
        %if objects.index(plp) < len(objects) - 1:
            <p style="page-break-after:always"/>
            <br/>
        %endif
    %endfor
</body>
</html>
